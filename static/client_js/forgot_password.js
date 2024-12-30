import { log, emailValidatortoast, callAjax, fieldsValidator, removeError, sweetAlertMsg, showToastMsg }  from '../Common/common.js';


window.removeError = removeError;
//////////////// otp input validations
const inputs = document.querySelectorAll(".otp-field > input");
const button = document.querySelector("#verifyOTPBtn");



window.addEventListener("load", () => inputs[0].focus());
button.setAttribute("disabled", "disabled");

inputs[0].addEventListener("paste", function (event) {
  event.preventDefault();

  const pastedValue = (event.clipboardData || window.clipboardData).getData(
    "text"
  );
  const otpLength = inputs.length;

  for (let i = 0; i < otpLength; i++) {
    if (i < pastedValue.length) {
      inputs[i].value = pastedValue[i];
      inputs[i].removeAttribute("disabled");
      inputs[i].focus;
    } else {
      inputs[i].value = ""; // Clear any remaining inputs
      inputs[i].focus;
    }
  }
});

inputs.forEach((input, index1) => {
  const currentInput = input;
  const nextInput = input.nextElementSibling;
  const prevInput = input.previousElementSibling;
  
  input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace") {
        inputs.forEach((input, index2) => {
            if (index1 <= index2 && prevInput) {
              
              if (input.value == "")
              {
                input.setAttribute("disabled", true);
                prevInput.value = "";
                prevInput.focus();
              }
              input.value = "";
            }
        });
    }
  });

  input.addEventListener("keyup", (e) => {
    if (currentInput.value.length > 1) {
        currentInput.value = "";
        return;
    }

    if (
        nextInput &&
        nextInput.hasAttribute("disabled") &&
        currentInput.value !== ""
    ) {
        nextInput.removeAttribute("disabled");
        nextInput.focus();
    }

    button.classList.remove("active");
    button.setAttribute("disabled", "disabled");

    const inputsNo = inputs.length;
    if (!inputs[inputsNo - 1].disabled && inputs[inputsNo - 1].value !== "") {
      button.classList.add("active");
      button.removeAttribute("disabled");
      return;
    }
  });
});

function validateEmail(email) {
  // Define the regular expression pattern for allowed domains
  const pattern = /^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com)$/;
  
  // Test the email against the pattern
  return pattern.test(email);
}



window.removeError = removeError;

window.sendOtp = async function(_this, email)
{
    // debugger;
    var get_email = $("#"+email).val();
    var fields = await emailValidatortoast(email)
    if (fields)
    {
        var data = {"email":get_email}
        var response = await callAjax('/send_otp/', data,_this, 'Send OTP...', 'Save');

        if (response.status == 1)
        {
            showToastMsg('SUCCESS', response.msg, 'success');
            window.checkOTP = response.otp;
            $('.credentials-container').hide();
            $('.login-container').hide();
            $('#otp-container').show(400);
            $('#firstInput').focus();
            window.user_id = response.user_id
        }
        else if (response.status == 2)
        {
            $('#'+email).focus();
            showToastMsg('Warning', response.msg, 'warning');
        }
        else
        {
            $('#'+email).focus();
            await showToastMsg('Error', response.msg, 'error');
        }
    }
}

$('#email').bind('keypress', function(e) 
{
	if(e.keyCode==13)
    {
		$('#login_btn').trigger('click');
	}
});
$('#enterHandle').bind('keypress', function(e) 
{
	if(e.keyCode==13)
    {
		$('#verifyOTPBtn').trigger('click');
	}
});



function getOTPValues() {
  var otpValues = '';
  
  $('.otp-field input[type="number"]').each(function() {
      otpValues += $(this).val();
  });

  return otpValues;
}

window.verfyOTP = async function(_this)
{
  let otpValues = getOTPValues();

  if (otpValues == window.checkOTP.toString())
  {
    
    $('.login-container').hide();
    $('#otp-container').hide();
    $("#forgotPass_div").show()

  }
  else
  {
    showToastMsg('ERROR', 'Invalid OTP. Please check and try again.', 'error');
    $('#enterHandle').focus();
  }
}



window.TogglePassword1 = function()
{
        const password1 = document.querySelector('#confirm_password'); 
        const type = password1.getAttribute('type') === 'password' ?
        
        'text' : 'password';
                
        password1.setAttribute('type', type);
        
        if (type == "text")
        {
            
            $("#new_password").removeClass("mdi-eye-off-outline");
            $("#new_password").addClass("mdi-eye-outline");
        }
        else
        {
            
            $("#new_password").removeClass("mdi-eye-outline");
            $("#new_password").addClass("mdi-eye-off-outline");
        }
}






function validatePassword(password) 
{
    const passwordPattern = /^(?=.*\d)(?=.*[\W_]).{6,10}$/;
    return passwordPattern.test(password);
}

window.forgotPasswordfunc = async function(_this,password,confirm_password)
{
    var fields_validate = await fieldsValidator([password,confirm_password])
    if (fields_validate)
    {
        if (fields_validate['password'] ==  fields_validate['confirm_password'])
        {
            var validate_password = validatePassword(fields_validate['password'])

            if (validate_password)
            {
                fields_validate['user_id'] = user_id
                var response = await callAjax('/forgotPasswordAjax/',fields_validate,_this, 'Loading...', 'Save' );
                if (response.status == 1)
                {
                    
                    await sweetAlertMsg("Saved Successfully",response.msg ,"success");
                    location.href="/Login/"
                    // setTimeout(  function() {
                    // }, 2000);
                }
                else
                {
                    sweetAlertMsg("Error",response.msg,"error");
                }
            }
            else
            {
                sweetAlertMsg("Error","Password must contain at least one number, one special character, and be 6 to 10 characters in length..","error");
            }
            
            
        }
        else
        {
            sweetAlertMsg("Password Mismatch","New password and confirm password does not match.","error");
        }
    }
}