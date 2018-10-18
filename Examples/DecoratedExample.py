# coding=utf8
import json
import bottle
from beaker.middleware import SessionMiddleware
from bottleLdap import Auth
from SampleSettings import LDAP_SERVER, LDAP_DOMAIN, LDAP_SEARCH, SESSION_KEY, ROLE_LIST, BIND_HOST, BIND_PORT

# Initialize the Auth class with our LDAP settings
auth = Auth(ldap_server=LDAP_SERVER, ldap_domain=LDAP_DOMAIN,
            search_domain=LDAP_SEARCH)


# alias the authorization decorator with defaults
authorize = auth.make_auth_decorator(fail_redirect="/login", role="admin")  # You probably don't want your default role to be admin...

# Setup the application with session options
app = bottle.app()
session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': SESSION_KEY,
    'session.httponly': False,
    'session.timeout': 3600 * 24 * 7,  # 7 days
    'session.type': 'cookie',
    'session.validate_key': True,
}

# Install the beaker middleware
app = SessionMiddleware(app, session_opts)


# #  Bottle methods  # #
def postd():
    return bottle.request.forms


def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()


@bottle.post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    auth.login(username, password, success_redirect='/',
               fail_redirect='/login')


@bottle.route('/logout')
def logout():
    auth.logout(success_redirect='/login')


@bottle.get('/access_denied')
@bottle.view('access_denied')
@authorize(fail_redirect='/login')
def access_denied():
    return {}

# Admin-only pages
@bottle.route('/admin')
@authorize(role="admin", fail_redirect='/access_denied')
@bottle.view('admin_page')
def view_admin_page():
    """Only admin users can see this"""
    return dict(
        userlist=auth.list_user_roles(),
        role_list=ROLE_LIST
    )


@bottle.post('/ajax-admin/user-role')
@authorize(role="admin", fail_redirect='/access_denied')
def admin_user_role():
    data = bottle.request.json
    auth.update_user_role(data)
    return json.dumps({'code': 0, 'message': 'User role successfully updated'})


# Special-only pages
@bottle.route('/special')
@authorize(role="special", fail_redirect='/access_denied')
@bottle.view('special_page')
def view_special_page():
    return {}


# Static pages
@bottle.route('/login')
@bottle.view('login_form')
def login_form():
    """Serve login form"""
    return {}


@bottle.get('/static/<route>/<file>')
def get_resource(route, file):
    return bottle.static_file(file, root='./static/{0}'.format(route))


# My Pages
@bottle.route('/')
@authorize()
@bottle.view('index')
def index():
    return {'short_name': auth.current_user.short_name}

# #  Web application main  # #


def main():
    bottle.debug(True)
    bottle.run(app=app, quiet=False, reloader=False,
               host=BIND_HOST, port=BIND_PORT)


if __name__ == "__main__":
    main()
