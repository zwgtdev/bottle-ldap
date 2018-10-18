<html>

<head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
    <link href="/static/css/font-awesome.min.css" rel="stylesheet">
    <link href="/static/css/bootstrap-msg-standalone-0.4.0.min.css" rel="stylesheet">
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
    <title>bottle-ldap Demo Login</title>
</head>

<body>
    <div class="container">
        <h2>bottleLdap demo</h2>
        <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="login" role="tabpanel" aria-labelledby="login-tab">
                <h3>Login</h3>
                <p>Please use your domain credentials:</p>
                <form action="login" method="post" name="login">
                    <div class="form-group">
                        <label for="inputUsername">Username</label>
                        <input type="text" class="form-control" name="username" id="inputUsername" placeholder="Enter Username">
                    </div>
                    <div class="form-group">
                        <label for="inputPassword">Password</label>
                        <input type="password" class="form-control" name="password" id="inputPassword" placeholder="Password">
                    </div>
                    <button type="submit" class="btn btn-dark"> OK </button>
                </form>
            </div>
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-2.2.4.min.js" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js" integrity="sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js" integrity="sha384-h0AbiXch4ZDo7tp9hKZ4TsHbi047NrKGLO3SEJAg45jXxnGIfYzk4Si90RDIqNm1" crossorigin="anonymous"></script>
    <script src="/static/js/bootstrap-msg-0.4.0.min.js"></script>
</body>
    <script type="text/javascript">
        $(document).ready(function() {
            $( "input[ type='password' ]" ).keypress( function(e) {
                var key_check = e.which;
                var isUp = ( key_check >= 65 && key_check <= 90 ) ? true : false;
                var isLow = ( key_check >= 97 && key_check <= 122 ) ? true : false;
                var isShift = ( e.shiftKey ) ? e.shiftKey : ( ( key_check == 16 ) ? true : false );
                if ( ( isUp && !isShift ) || ( isLow && isShift ) ) {
                    // capLock();
                    Msg.show('Caps-lock is On!', 'warning', 5000);
                    console.log('Caps on');
                };
            });
        });
    </script>
</html>