import { log, callAjax, emailValidatortoast, filedValidatorToastmsg,removeError,sweetAlertMsg, showToastMsg } from '../CommonJS/common.js';
$(document).ready(function () {
    $(document).bind("keypress", function (e) {
      if (e.keyCode == 13) {
        $("#client_login_btn").trigger("click");
      }
    });
});




window.removeError = removeError;

window.LoginHandler = async function(_this,email,admin_password)
{
    // var isCheck = $("#disclaimer_checkbox").prop('checked');
    // if (!isCheck) {
    //   $("#disclaimer_checkbox").focus();  
    //   $("#disclaimer_error").css('display', 'block');  
    //   return  ;
    // } 

    var email_fields = await emailValidatortoast(email)
    if(email_fields)
    {
        var fields_validate = await filedValidatorToastmsg([admin_password])
        if (fields_validate)
        {
            var response = await callAjax('/login_handler/', {'email': email_fields, 'password': $("#admin_password").val()}, _this, 'Please wait', 'Log in')
        
            if (response.status == 1)
            {
                sessionStorage.setItem('user_id', response.user_id)
                $("#user_id").val(response.user_id)
                location.href = '/index'
            }
            else if (response.status == 2)
            {
                showToastMsg('Blocked', response.msg, 'warning')
            }
            else
            {
                showToastMsg('Error', response.msg, 'error')
            }
        }
        
    }
        
    
}

// $('#email').bind('keypress', function(e) {
// 	if(e.keyCode==13){
//         var logbtn = document.getElementById("logged_in_btn")
// 		LoginHandler(logbtn);
// 	}
// });

// $('#admin_password').bind('keypress', function(e) {
//     if(e.keyCode==13){
//         var logbtn = document.getElementById("logged_in_btn")
//         LoginHandler(logbtn);
// 	}
// });