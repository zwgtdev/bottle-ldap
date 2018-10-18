% rebase('template_base.tpl', title='Admin UI')
<div class="container-fluid">
  <div class="row">
    <div class="col-md-12">
      &nbsp;
    </div>
  </div>
  <h2>Admin Page</h2>
  <div class="row">
    <div class="col-md-5">
      <h4>User Role Management</h4>
      <table class="table table-sm table-dark">
        <thead>
          <tr>
            <th>Username</th>
            %for role in role_list:
            <th>{{role}}</th>
            %end
          </tr>
        </thead>
        <tbody>
          %for user in userlist:
            %userroles = userlist.get(user)
            <tr>
              <td>{{user}}</td>
              %for role in role_list:
                %if role in userroles:
                  %checked_state="checked"
                %else:
                  %checked_state=""
                %end
                <td style="text-align: center;">
                  <input class="form-check-input cb-user-role" type="checkbox" role="{{role}}" username="{{user}}" {{checked_state}}>
                </td>
              %end
            </tr>
            %end
        </tbody>
      </table>
    </div>
  </div>
</div>
    <script>
      $('.cb-user-role').click(function(){
        var username = $(this).attr('username');
        var ischecked = $(this).is(':checked');
        var role = $(this).attr('role');
        $.ajax({
            type: "POST",
            url: "/ajax-admin/user-role",
            data: JSON.stringify({ username: username, state: ischecked, role: role }),
            contentType: "application/json; charset=utf-8",
            success: function(resultdata){
                var json_data = JSON.parse(resultdata)
                if (json_data.code == 1){
                  notification_error(json_data.message);
                }
                if (json_data.code == 0){
                  notification_success(json_data.message);
                }
            },
            failure: function(errMsg) {
                notification_error(errMsg);
            }
        });

      });
    </script>



