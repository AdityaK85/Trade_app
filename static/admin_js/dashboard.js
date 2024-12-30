import {log, callAjax, sweetAlertMsg, showToastMsg} from '../CommonJS/common.js';

$("#dashboard").addClass("active");

window.save = async function() {

    var client_id = $('#client_id').val();
    var password = $('#password').val();
    var vendor_code = $('#vendor_code').val();
    var app_key = $('#app_key').val();
    var totp = $('#totp').val();
    
    
    if (client_id.trim() === "") {

        showToastMsg("Client ID", "Please enter Client ID.", 'error');
        $('#client_id').focus()
    }
    else if (password.trim() === "") {

        showToastMsg("Password", "Please enter Password", 'error');
        $('#password').focus()
    }
    else if (vendor_code.trim() === "") {

        showToastMsg("Client Secret", "Please enter vendor code", 'error');
        $('#client_secret').focus()
    }
    else if (app_key.trim() === "") {

        showToastMsg("APP ID", "Please enter app key", 'error');
        $('#app_id').focus()
    }
    else if (totp.trim() === "") {

        showToastMsg("TOTP", "Please enter totp string", 'error');
        $('#totp').focus()
    }
    else {

        $("#loader-container").fadeIn("slow");
        var data = {
            'client_id': client_id,
            'password': password,
            'vendor_code': vendor_code,
            'app_key': app_key,
            'totp': totp,
        }

        var response = await callAjax('/save_broker_aj/',data );

        if (response.status == 1)
        {
            $("#loader-container").fadeOut("slow");
            showToastMsg('Sucess',response.msg, 'success'); 
			await new Promise(resolve => setTimeout(resolve, 1500)); 
			location.reload();
            
        }
        else if (response.status == 0)
        {
            $("#loader-container").fadeOut("slow");
            showToastMsg("Error", response.msg, 'error')
        }
        else{
            $("#loader-container").fadeOut("slow");
            showToastMsg("Error", 'Something Went Wrong...', 'error')
        }
    }
}







window.GenerateToken = async function(this_){
    var  response = await callAjax('/generate_token/', {}, this_, 'Generating...', 'Generated', false)
    if (response.status == 1){
        await sweetAlertMsg('Generated', response.msg, 'success')
        await location.reload()
    }
    else{
        sweetAlertMsg('Error', response.msg, 'error')
    }
}