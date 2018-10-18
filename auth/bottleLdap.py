import bottle
import ldap
import sys
import os
import json
from collections import OrderedDict


class AAAException(Exception):
    """Generic Authentication/Authorization Exception"""
    pass


class AuthException(AAAException):
    """Authentication Exception: incorrect username/password pair"""
    pass


class UserExists(AAAException):
    pass


class JsonRoleStore(object):
    """Json based role store"""

    def __init__(self, directory, filename='roles.json'):
        self.directory = directory
        self.filename = filename
        self._pathfinder()
        self._load_roles()

    def _pathfinder(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(os.path.join(self.directory, self.filename)):
            self._save_roles({})

    def _load_roles(self):
        try:
            with open(os.path.join(self.directory, self.filename), 'r') as role_file:
                self.roles = json.loads(role_file.read())
        except:
            self.roles = OrderedDict()

    def _save_roles(self, data):
        with open(os.path.join(self.directory, self.filename), 'w') as json_file:
            json_file.write(json.dumps(data))
        self._load_roles()

    def update_user_roles(self, role_data):
        self._save_roles(role_data)


class BaseAuth(object):
    """BaseAuth is an authentication module that uses AD to authenticate a user."""

    def __init__(self, ldap_server, ldap_domain, session_key_name=None, session_domain=None, search_domain=None):
        """Auth class
        :param ldap_server: ldap server address
        :type ldap_server: str.
        :param ldap_domain: ldap domain name
        :type ldap_domain: str.
        """
        super(BaseAuth, self).__init__()
        self.ldap_server = ldap_server
        self.ldap_domain = ldap_domain
        self.search_domain = search_domain
        self.session_key_name = session_key_name or 'beaker.session'
        self.session_domain = session_domain
        self._store = JsonRoleStore('users')

    def login(self, username, password, success_redirect=None,
              fail_redirect=None):
        """Check login credentials for an existing user.
        Optionally redirect the user to another page (typically /login)

        :param username: username
        :type username: str or unicode.
        :param password: cleartext password
        :type password: str.or unicode
        :param success_redirect: redirect authorized users (optional)
        :type success_redirect: str.
        :param fail_redirect: redirect unauthorized users (optional)
        :type fail_redirect: str.
        :returns: True for successful logins, else False
        """
        # assert isinstance(username, type(u'')), "username must be a string"
        # assert isinstance(password, type(u'')), "password must be a string"

        auth_res, user_details = self._verify_password(
            username,
            password,
        )
        if auth_res == 'Authenticated':
            # Setup session data
            self._setup_cookie(username, user_details)
            self._check_roles(username)
            if success_redirect:
                self._redirect(success_redirect)
            return True

        if fail_redirect:
            self._redirect(fail_redirect)

        return False

    def logout(self, success_redirect='/login', fail_redirect='/login'):
        """Log the user out, remove cookie

        :param success_redirect: redirect the user after logging out
        :type success_redirect: str.
        :param fail_redirect: redirect the user if it is not logged in
        :type fail_redirect: str.
        """
        try:
            session = self._beaker_session
            session.delete()
        except Exception as e:
            log.debug("Exception %s while logging out." % repr(e))
            self._redirect(fail_redirect)

        self._redirect(success_redirect)

    def make_auth_decorator(self, role=None,
                            fail_redirect='/login'):
        '''
        Create a decorator to be used for authentication and authorization

        :param username: A resource can be protected for a specific user
        :param role: Minimum role level required for authorization
        :param role: Only this role gets authorized
        :param fail_redirect: The URL to redirect to if a login is required.
        '''
        session_manager = self

        def auth_require(role=role,
                         fail_redirect=fail_redirect):
            def decorator(func):
                import functools

                @functools.wraps(func)
                def wrapper(*a, **ka):
                    session_manager.require(
                        role=role,
                        fail_redirect=fail_redirect)
                    return func(*a, **ka)
                return wrapper
            return decorator
        return(auth_require)

    def require(self, role=None,
                fail_redirect=None):
        """Ensure the user is logged in has the required role (or higher).
        Optionally redirect the user to another page (typically /login)
        If both `username` and `role` are specified, both conditions need to be
        satisfied.
        If none is specified, any authenticated user will be authorized.
        By default, any role with higher level than `role` will be authorized;
        set role=True to prevent this.

        :param role: require user role to match `role` strictly
        :type role: bool.
        :param redirect: redirect unauthorized users (optional)
        :type redirect: str.
        """
        # Parameter validation
        # Authentication
        try:
            cu = self.current_user
        except AAAException:
            if fail_redirect is None:
                raise AuthException("Unauthenticated user")
            else:
                self._redirect(fail_redirect)
        if role:
            # A specific role is required
            if role in self.current_user.roles:
                return

            if fail_redirect is None:
                raise AuthException("Unauthorized access: incorrect role")

            self._redirect(fail_redirect)

            if fail_redirect is None:
                raise AuthException("Unauthorized access: ")

            self._redirect(fail_redirect)

        return  # success

    def list_user_roles(self):
        """List users.

        :return: (username, roles) generator (sorted by
            username)
        """
        return self._store.roles

    def list_users(self):
        return self._store.roles.keys()

    def update_user_role(self, data):
        user_roles = self._store.roles.get(data.get('username').lower())
        if not data.get('state'):
            user_roles.remove(data.get('role'))
        else:
            user_roles.append(data.get('role'))
        self._store.roles[data.get('username').lower()] = user_roles
        self._store.update_user_roles(self._store.roles)

    @property
    def current_user(self):
        """Current autenticated user

        :returns: User() instance, if authenticated
        :raises: AuthException otherwise
        """
        session = self._beaker_session
        username = session.get('username', None)
        if username is None:
            raise AuthException("Unauthenticated user")
        if username is not None:
            return User(username, self, session=session)
        raise AuthException("Unknown user: %s" % username)

    @property
    def user_is_anonymous(self):
        """Check if the current user is anonymous.

        :returns: True if the user is anonymous, False otherwise
        :raises: AuthException if the session username is unknown
        """
        try:
            username = self._beaker_session['username']
        except KeyError:
            return True

        return False

    def _check_roles(self, username):
        if username.lower() not in [x.lower() for x in self._store.roles.keys()]:
            self._store.roles[username.lower()] = ['user']
            self._store.update_user_roles(self._store.roles)

    def _verify_password(self, username, password):
        """Verify credentials
        :param username: AD Username
        :type username: str.
        :param password: AD Password
        :type password: str.
        """
        try:
            try:
                conn = ldap.initialize(
                    'ldap://{0}'.format(self.ldap_server), bytes_mode=True)
            except:
                conn = ldap.initialize(
                    'ldap://{0}'.format(self.ldap_server), bytes_mode=False)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.simple_bind_s('{0}@{1}'.format(
                username, self.ldap_domain), password)
            user_details = conn.search_s(self.search_domain,
                                         ldap.SCOPE_SUBTREE, 'userPrincipalName=%s@%s' % (username, self.ldap_domain), ['mail', 'givenname', 'cn'])[0][1]
            for key in user_details:
                user_details[key] = user_details.get(key)[0]

        except ldap.INVALID_CREDENTIALS:
            return "Your credentials are invalid", None
        except ldap.SERVER_DOWN:
            return "The AD server appears to be down", None
        except ldap.LDAPError as e:
            if type(e.message) == dict and e.message.has_key('desc'):
                return e.message['desc'], None
            else:
                return e, None
        else:
            conn.unbind_s()
            return 'Authenticated', user_details

    def _setup_cookie(self, username, user_details):
        """Setup cookie for a user that just logged in"""
        session = self._beaker_session
        session['username'] = username.lower()
        session['short_name'] = user_details.get('givenName')
        session['full_name'] = user_details.get('cn')
        session['email'] = user_details.get('mail')
        if self.session_domain is not None:
            session.domain = self.session_domain
        self._save_session()


class User(object):

    def __init__(self, username, auth_obj, session=None):
        """Represent an authenticated user, exposing useful attributes:
        username, role, level, description, email_addr, session_creation_time,
        session_accessed_time, session_id. The session-related attributes are
        available for the current user only.

        :param username: username
        :type username: str.
        :param auth_obj: instance of :class:`Auth`
        """
        self._auth = auth_obj
        self.username = username.lower()
        self.short_name = session.get('short_name', None)
        self.full_name = session.get('full_name', None)
        self.email = session.get('email', None)
        self.roles = self._auth._store.roles.get(self.username, [])


class Auth(BaseAuth):
    @staticmethod
    def _redirect(location):
        bottle.redirect(location)

    @property
    def _beaker_session(self):
        """Get session"""
        return bottle.request.environ.get(self.session_key_name)

    def _save_session(self):
        self._beaker_session.save()
