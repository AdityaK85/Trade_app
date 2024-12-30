import { log, emailValidator,filedValidator, callAjax, fieldsValidator, removeError, resetControls,sweetAlertMsg, showToastMsg } from '../Common/common.js';

window.removeError = removeError


var preloader = document.getElementById("preloader");
var loader_status = document.getElementById("status");


window.show_loader = function(){
    preloader.style.display = 'block';
    loader_status.style.display = 'block';
}

window.hide_loader = function(){
    preloader.style.display = 'none';
    loader_status.style.display = 'none';
}

window.brokerLogin = async function (app_id)
{
	var url = 'https://masterswift-beta.mastertrust.co.in/oauth2/auth?scope=orders%20holdings&state=%7B%22param%22:%22value%22%7D&redi-rect_uri=http://127.0.0.1&response_type=code&client_id='+app_id;
	if (url)window.location.href = url;
}

window.saveBrokerAccount = async function (_this, fields_arr)
{
	var fields = await fieldsValidator(fields_arr);

	if (fields)
	{
		fields['fk_user'] = $('#user_id').val();
		let response = await callAjax('/saveBrokerAccount/', fields, _this, 'Please wait', 'Verify');

		if (response.status == 1 )
		{
			brokerLogin(response.app_id);
		}
		else
		{
			await sweetAlertMsg('ERROR', response.msg, 'error');
		}
		// showToastMsg('SUCCESS', 'done', 'success')
	}
}




window.changeTextType = async function(fieldsArr , this_)
{
	for (let item of fieldsArr)
	{
		if ($('#'+item).attr('type') == 'text')
		{
			$('#'+item).attr('type', 'password');
            this_.classList.remove('fa-eye');
            this_.classList.add('fa-eye-slash');

		}
		else
		{
			$('#'+item).attr('type', 'text');
            this_.classList.add('fa-eye');
            this_.classList.remove('fa-eye-slash');
		}
	}
}


// redirect to broker login


window.set_target_sl = async function( save_type, target_sl_value , input_id , tradingMode){

	var response = await callAjax('/set_target_sl/', {'save_type': save_type, 'target_sl_value': target_sl_value , 'tradingMode' : tradingMode } );
	if (response.status == 1)
	{	
		$('#'+input_id).html(response.tsl_value);
		await showToastMsg(save_type, response.msg, 'success');
	}
	else {

		await showToastMsg('ERROR', response.msg, 'error');
	}

}


window.edit_target_sl = function(showed_value, edit_value, save_btn, edit_btn){
	document.getElementById(showed_value).style.display = 'none';
	document.getElementById(edit_value).style.display = 'inline';
	document.getElementById(save_btn).style.display = 'inline';
	document.getElementById(edit_btn).style.display = 'none';
}


window.save_target_sl = function(showed_value, update_input, save_btn, edit_btn, set_type, tradingMode){

	var update_val = $('#'+update_input).val();
	document.getElementById(showed_value).style.display = 'inline';
	document.getElementById(showed_value).textContent = update_val;
	document.getElementById(update_input).textContent = "";
	document.getElementById(update_input).style.display = 'none';
	document.getElementById(save_btn).style.display = 'none';
	document.getElementById(edit_btn).style.display = 'inline';
	set_target_sl(set_type, update_val , showed_value ,tradingMode)

}


window.change_trade_mode_backend = async function(trade_mode){
	show_loader()

	var response = await callAjax('/change_trade_mode/', {'trade_mode': trade_mode} );

	if (response.status == 1){
		hide_loader()
		await sweetAlertMsg(response.title, response.msg, 'success');
		location.reload()
	}
	else if (response.status == 2){
		hide_loader()
		var accessAlert = await sweetAlertMsg('Paper Mode Unavailable', response.msg, 'question', 'cancel', 'Subscribe')
		if (accessAlert){
			
			window.open('https://superprofile.bio/vp/670e7cacbe8a640013b28990', '_blank')
		}
		else{
			location.reload()
		}
	}

}


window.change_trading_mode = async function(this_, is_trade_mode) {
   
	const isChecked = this_.checked;
	const status = isChecked ? 'Are you sure you want to change to Live mode?' : 'Are you sure you want to change to Paper mode?';
	const title = `Change ${isChecked ? 'Live' : 'Paper'} Trading`;
	var alert = await sweetAlertMsg(title, status, 'question', 'cancel', 'Yes');
	
	if (alert) {
		
		if (is_trade_mode == 'true') {
			
			change_trade_mode_backend(false)
		}
		else {
			change_trade_mode_backend(true)
		}
		
	} 
	else {

		location.reload()	

	}
};


window.reset_trades = async function(user_id) {

	var alert = await sweetAlertMsg('Reset Trades', 'This action removes all your closed and pending trades', 'question', 'cancel', 'Yes');
	if (alert) {
		var response = await callAjax('/reset_trades/', {'user_id': user_id});
		if (response.status == 1) {
			await showToastMsg('Success', response.msg, 'success');
			location.reload();
		}
		else {
			await showToastMsg('Error', response.msg, 'error');
		}
	}
}


document.addEventListener('DOMContentLoaded', function() {

	var niftyTab = document.getElementById('niftyTab');
	var bankNiftyTab = document.getElementById('bankNiftyTab');

	niftyTab.addEventListener('click', function(event) {
		console.log('NIFTY tab clicked');
	});

	bankNiftyTab.addEventListener('click', function(event) {
		console.log('BANKNIFTY tab clicked');
	});
});