import { log, emailValidator, callAjax, fieldsValidator, removeError, resetControls,sweetAlertMsg, showToastMsg, filedValidatorToastmsg,emailValidatortoast,} from '../Common/common.js';

window.removeError = removeError;


window.signup = async function(_this,inputname,inputemail,inputmobile_no)
{
    
    
    // var email_fields = await emailValidatortoast(email)
    // if (email_fields)
    // {

        var emailfilter = /^\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b$/i;
        var fieldname = $(`#${inputname}`).val()
        var fieldemail = $(`#${inputemail}`).val()
        var fieldmobile_no = $(`#${inputmobile_no}`).val()


        if ( fieldname.trim() == '' ) {
            showToastMsg('Name', 'Please enter your name', 'error');
        }

        else if ( fieldmobile_no.trim() == '' ) {
            showToastMsg('Mobile Number', 'Please enter your mobile number', 'error');
        }

        else if ( fieldmobile_no.length < 10 ) {
            showToastMsg('Mobile Number', 'Please enter 10 digit mobile number', 'error');
        }

        else if ( fieldemail.trim() == '' ) {
            showToastMsg('Email', 'Please enter your email', 'error');
        }

        else if (!emailfilter.test(fieldemail)) {
            showToastMsg('Email', 'Please enter your valid email', 'error');
        }

        else{
            var data = {"email":fieldemail,"name":fieldname,"mobile_no":fieldmobile_no}
            
    
            var response = await callAjax('/signupAjax/',data ,_this, 'Verifying...', 'Verify');
            if (response.status == 1)
            {
    
                await sweetAlertMsg("Success",response.msg,"success");
                // await showToastMsg("Success",response.msg,"success");
                // setTimeout(  function() {
                
                location.href="/Login/"
                // }, 2000);
            
            }
        
            else
            {
                showToastMsg("Error",response.msg,"error");
            }
        }
       
            
      
}