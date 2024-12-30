import { log, callAjax, fieldsValidator, removeError,sweetAlertMsg, showToastMsg } from '../CommonJS/common.js';

window.removeError = removeError;

window.toggle_confirmPass = async function  ()
{
    const password1 = document.querySelector('#confirm_password'); 
    const type = password1.getAttribute('type') === 'password' ?
    'text' : 'password';
    password1.setAttribute('type', type);
    if (type == "text") {
        $("#icon_confirm_pass").removeClass("mdi-eye-off-outline");
        $("#icon_confirm_pass").addClass("mdi-eye-outline");
    } else {
        $("#icon_confirm_pass").removeClass("mdi-eye-outline");
        $("#icon_confirm_pass").addClass("mdi-eye-off-outline");
    }
}


window.toggleOldPass = async function  ()
{
    const password1 = document.querySelector('#old_password'); 
    const type = password1.getAttribute('type') === 'password' ?   
    'text' : 'password';
    password1.setAttribute('type', type);
    if (type == "text") {
        $("#old_passicon").removeClass("mdi-eye-off-outline");
        $("#old_passicon").addClass("mdi-eye-outline");
    } else {
        $("#old_passicon").removeClass("mdi-eye-outline");
        $("#old_passicon").addClass("mdi-eye-off-outline");
    }
}

window.check_oldpass = async function(_this,user_id,old_password)
{
    if(user_id != "" && user_id != null)
    {
        var fields_validate = await fieldsValidator([old_password])
        if (fields_validate)
        {
            fields_validate['user_id'] = user_id
            var response = await callAjax('/checkOldPassAjax/',fields_validate,_this, 'Loading...', 'Save' );
            if (response.status == 1) {
                $("#oldPass_div").hide();
                $("#changePass_div").show(); 
            } else {
                showToastMsg("Error",response.msg,"error");
            }
        }
    }
}


function validatePassword(password) 
{
    const passwordPattern = /^(?=.*\d)(?=.*[\W_]).{6,10}$/;
    return passwordPattern.test(password);
}

window.changePass = async function(_this,user_id,new_password,confirm_password)
{
    if(user_id != "" && user_id != null)
    {
        var fields_validate = await fieldsValidator([new_password,confirm_password])
        
        if (fields_validate)
        {
            if (fields_validate['new_password'] ==  fields_validate['confirm_password'])
            {
                var validate_password = validatePassword(fields_validate['new_password'])

                if (validate_password)
                {
                    fields_validate['user_id'] = user_id
                    var response = await callAjax('/change_password/',fields_validate,_this, 'Loading...', 'Save' );
                    if (response.status == 1)
                    {
                        
                        await sweetAlertMsg("Success",response.msg,"success");
                        location.reload();
                        // setTimeout(  function() {
                           
                        // }, 1000);
                    }
                    else
                    {
                        showToastMsg("Error",response.msg,"error");
                    }
                }
                else
                {
                    showToastMsg("Error","Password must contain at least one number, one special character, and be 6 to 10 characters in length..","error");
                }
                
                
            }
            else
            {
                showToastMsg("Error","New password and confirm password does not match.","error");
            }
        }
    }
}



// --------------------------------------------CREATE DYMIC TD IN TABLES-------------------------------------------


window.update_existing_row = function(rowId, data ,parent_data_update, order_data_update, obj_id){
    const existingRow = document.getElementById(rowId);
    if (existingRow) {
        try {if (parent_data_update){existingRow.querySelector(`#strike_${obj_id}`).textContent = data.tradingSymbol || '-';}} catch (error) {}
        try {if (parent_data_update){existingRow.querySelector(`#cb_tf_${obj_id}`).textContent = data.cf_tf || '- | -'; }} catch (error) {}
        
        try {if (parent_data_update){ existingRow.querySelector(`#lot_size_${obj_id}`).textContent =  data.lot_size ; } } catch (error) {}

       

        // FULL TARGET DYMIC ELEMENT
        try {
          if (parent_data_update) {
            const fullTElement = existingRow.querySelector(`#full_target_${obj_id}`);
            const fullTiconExists = document.getElementById(`full_target_${obj_id}_icon`);
            
            if (data.full_target !== null) {
              fullTElement.innerHTML = data.full_target;
              fullTElement.classList.add('change_td_to_input');
              if (fullTiconExists) {
                fullTiconExists.style.display = 'none'; 
              }
            } else {
              fullTElement.innerHTML = '';
              if (!fullTiconExists) {
                fullTElement.innerHTML = `
                  <i onclick="
                    change_td_to_input(
                      this,
                      'full_target_${obj_id}',
                      'full_target_${obj_id}_icon',
                      'full_target',
                      '${obj_id}',
                      'lot_size_${obj_id}'
                    )" id="full_target_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;">
                  </i>`;
              }
              else if (data.full_target == null){
                fullTiconExists.style.display = 'block';
              }
            }
          }
        } catch (error) {
          console.error(error);
        }

   
        
        if (order_data_update) {
          const os_element = existingRow.querySelector(`#os_${obj_id}`);
          if (os_element) {
              os_element.textContent = data.order_side !== null ? data.order_side : '-';
          }
        }
        if (order_data_update){existingRow.querySelector(`#entry_${obj_id}`).textContent = data.entryPrice !== null ? data.entryPrice.toFixed(2) : '-'; }
        if (order_data_update){existingRow.querySelector(`#exit_${obj_id}`).textContent = data.exitPrice !== null ? data.exitPrice.toFixed(2) : '-';}
        if (order_data_update){existingRow.querySelector(`#realizedPNL_${obj_id}`).textContent = data.realizedPNL != null ? data.realizedPNL.toFixed(2) : '-';}
        if (order_data_update) {

            if (data.status == "OPEN") { 
                existingRow.querySelector(`#status_${obj_id}`).innerHTML = `<span style="font-size: 100%;" class="badge bg-success">OPEN</span> `;  
                existingRow.querySelector(`#action_${obj_id}`).innerHTML = `<a role="button" onclick="square_off_pos('${data.id}', '${data.order_mode}', this)"  title="Square Off"  role="button" class="btn btn-sm btn-primary"  style="width: auto;height: 100%;"   ><i class="fa-solid fa-arrow-right-from-bracket"></i></a> &nbsp<span class="mx-2" >${data.remark}</span>`;
            }
            else if (data.status == "CLOSED") { 
                existingRow.querySelector(`#status_${obj_id}`).innerHTML = `<span style="font-size: 100%;" class="badge bg-danger">CLOSED</span> `; 
                existingRow.querySelector(`#action_${obj_id}`).innerHTML = `<span class="mx-2" >${data.remark !== null ? data.remark : ''}</span>`; 
                existingRow.querySelector(`#pnl_${obj_id}`).innerHTML = "-";
                existingRow.querySelector(`#pnl_${obj_id}`).textContent = "-";
            }
            else if (data.status == "ERROR") { 
                existingRow.querySelector(`#status_${obj_id}`).innerHTML = `<span style="font-size: 100%;" class="badge bg-danger">ERROR</span> `; 
                existingRow.querySelector(`#action_${obj_id}`).innerHTML = `<span class="mx-2" >${data.remark !== null ? data.remark : ''}</span>`; 
                existingRow.querySelector(`#pnl_${obj_id}`).innerHTML = "-";
                existingRow.querySelector(`#pnl_${obj_id}`).textContent = "-";
            }
            else { 
                existingRow.querySelector(`#status_${obj_id}`).innerHTML = '<span style="font-size: 100%;" class="badge bg-danger">PENDING</span>';  
                existingRow.querySelector(`#action_${obj_id}`).innerHTML = `<a role="button" onclick="delete_pos('${obj_id}', '${data.order_mode}', this)" title="Delete" role="button" class="btn btn-sm btn-danger" style="width: auto;"> <i class="fa-solid fa-xmark"></i></a> `;   
            }
        }
    }
}


window.createTableRow = function (data, tableSelector, index_type) {
    var tr_id = 'tr_' + data.id;
    var obj_id = data.id;
    var parent_data_update = true;
    var order_data_update = false;
    
    if (data.id && data.entryPrice ){
        tr_id = 'tr_' + data.fk_strategy;
        obj_id = data.fk_strategy;
        order_data_update = true;
        parent_data_update = false
    }

    const existingRow = document.getElementById(tr_id);
    if (existingRow) {
        update_existing_row(tr_id, data, parent_data_update, order_data_update, obj_id);
        return;
      }
   

    const newRow = document.createElement('tr');
    newRow.classList.add('text-center');
    newRow.id = tr_id 
    newRow.innerHTML = `
      <td id="nfty_strike">${data.tradingSymbol || '-'}</td>
      
      
      <td id="lot_size_${obj_id}">${data.lot_size || '-'}</td>

      
      <td  style="width: 10%;"  id="stop_loss"  ><span class="mx-2 change_td_to_input" data-id='${obj_id}' data-type="stop_loss"  style="display: flex;justify-content: center;cursor: pointer" id="stop_loss_${obj_id}" >${data.stop_loss != null ? data.stop_loss.toFixed(2) : ''}</span> 
        <i onclick="
        change_td_to_input(
        this, 
        'stop_loss_${obj_id}', 
        'stop_loss_${obj_id}_icon', 
        'stop_loss', 
        '${obj_id}', 
        'lot_size_${obj_id}')" id="stop_loss_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer; ${data.stop_loss ? 'display:none' : ''} "></i></td>

      <td style="width: 10%;" id="full_target">
        <span class="mx-2 change_td_to_input" data-id="${obj_id}" data-type="full_target" style="display: flex; justify-content: center; cursor: pointer" id="full_target_${obj_id}">
          ${data.full_target || ''}
        </span>
        <i onclick="
          change_td_to_input(
            this,
            'full_target_${obj_id}',
            'full_target_${obj_id}_icon',
            'full_target',
            '${obj_id}',
            'lot_size_${obj_id}'
          )" id="full_target_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;${data.full_target ? 'display:none' : ''}">
        </i>
      </td>

      
      <td style="font-weight: bold; width: 95px; min-width: 74px;" class="nfty_${data.subscribe_token}_ltp">-</td> <!-- Placeholder for LTP -->
      <td style="width: 74px; min-width: 95px;" id="pnl_${obj_id}" id="nfty_mtm">-</td>
      
      <td id="entry_${obj_id}">-</td>
      <td id="exit_${obj_id}">-</td>
      <td id="status_${obj_id}">
        <span style="font-size: 100%;" class="badge bg-warning">Pending</span>
      </td>
      <td style="width: 74px; min-width: 74px;" id="realizedPNL_${obj_id}" >-</td>
      <td id="action_${obj_id}" style="display: flex;">
        <a role="button" onclick="delete_pos('${obj_id}', '', this)" title="Delete" role="button" class="btn btn-sm btn-danger" style="width: auto;">
          <i class="fa-solid fa-xmark"></i>
        </a>
      </td>
    `;

    const tableBody = document.querySelector(tableSelector);
    if (tableBody) {
      tableBody.insertBefore(newRow, tableBody.firstChild);
    } else {
      console.error(`Table body not found for selector: ${tableSelector}`);
    }
  }

window.update_high_price = function(obj_id, tr_data){
  const highPElement = document.getElementById(`high_price_${obj_id}`)
  const hPIconExists = document.getElementById(`high_price_${obj_id}_icon`);
  
  if (tr_data.high_price !== null) {
      highPElement.classList.add('change_td_to_input');
      highPElement.innerHTML = tr_data.high_price;
      if (hPIconExists) {
          hPIconExists.style.display = 'none';
      }
  } else {
      highPElement.innerHTML = '';
      if (!hPIconExists) {
          highPElement.innerHTML = `
              <i onclick="
                  change_td_to_input(
                      this,
                      'high_price_${obj_id}',
                      'high_price_${obj_id}_icon',
                      'high_price',
                      '${obj_id}',
                      'lot_size_${obj_id}'
                  )" 
                  id="high_price_${obj_id}_icon" 
                  class="fas fa-pencil-alt edit-icon" 
                  style="cursor: pointer;">
              </i>`;
      } else {
          if (tr_data.high_price === null) {
              hPIconExists.style.display = 'block';
          }
      }
  }
}

window.update_low_price = function(obj_id, tr_data){

  const lowPElement = document.getElementById(`low_price_${obj_id}`)
  const lPIconExists = document.getElementById(`low_price_${obj_id}_icon`);
  if (tr_data.low_price !== null) {
    lowPElement.classList.add('change_td_to_input');
    lowPElement.innerHTML = tr_data.low_price;
    if (lPIconExists) {
      lPIconExists.style.display = 'none'; 
    }
  } else {
    lowPElement.innerHTML = '';
    if (!lPIconExists) {
      lowPElement.innerHTML = `
        <i onclick="
          change_td_to_input(
            this,
            'low_price_${obj_id}',
            'low_price_${obj_id}_icon',
            'low_price',
            '${obj_id}',
            'lot_size_${obj_id}'
          )" id="low_price_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;">
        </i>`;
    }
    else if (tr_data.low_price == null ){
      lPIconExists.style.display = 'block';
    }
  }
}

window.update_stoploss_price = function(obj_id, tr_data){
  const sLElement = document.getElementById(`stop_loss_${obj_id}`)
  const sLIconExists = document.getElementById(`stop_loss_${obj_id}_icon`);

  if (tr_data.stop_loss !== null) {
    sLElement.innerHTML = tr_data.stop_loss;
    sLElement.classList.add('change_td_to_input');
    if (sLIconExists) {
      sLIconExists.style.display = 'none'; 
    }
  } else {
    sLElement.innerHTML = '';
    if (!sLIconExists) {
      sLElement.innerHTML = `
        <i onclick="
          change_td_to_input(
            this,
            'stop_loss_${obj_id}',
            'stop_loss_${obj_id}_icon',
            'stop_loss',
            '${obj_id}',
            'lot_size_${obj_id}'
          )" id="stop_loss_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;">
        </i>`;
    }
    else if (tr_data.stop_loss == null){
      sLIconExists.style.display = 'block';
    }
  }
}

window.update_order_side = function(obj_id, tr_data){
  const sLElement = document.getElementById(`os_${obj_id}`)
  if (sLElement) {
    if (tr_data.order_side !== null) {
      sLElement.innerHTML = tr_data.order_side;
    } else {
      sLElement.innerHTML = '-';
    }
  }
}

window.update_fulltarget = function(obj_id, tr_data){
  const sLElement = document.getElementById(`full_target_${obj_id}`)
  const sLIconExists = document.getElementById(`full_target_${obj_id}_icon`);
  if (tr_data.full_target !== null) {
    sLElement.innerHTML = tr_data.full_target;
    sLElement.classList.add('change_td_to_input');
    if (sLIconExists) {
      sLIconExists.style.display = 'none'; 
    }
  } else {
    sLElement.innerHTML = '';
    if (!sLIconExists) {
      sLElement.innerHTML = `
        <i onclick="
          change_td_to_input(
            this,
            'full_target_${obj_id}',
            'full_target_${obj_id}_icon',
            'full_target',
            '${obj_id}',
            'full_target_${obj_id}'
          )" id="full_target_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;">
        </i>`;
    }
    else if (tr_data.full_target == null){
      sLIconExists.style.display = 'block';
    }
  }
}

window.update_partial_exit = function(obj_id, tr_data){
  const sLElement = document.getElementById(`partial_exit_${obj_id}`)
  const sLIconExists = document.getElementById(`partial_exit_${obj_id}_icon`);
  if (tr_data.partial_exit !== null) {
    sLElement.innerHTML = tr_data.partial_exit;
    sLElement.classList.add('change_td_to_input');
    if (sLIconExists) {
      sLIconExists.style.display = 'none'; 
    }
  } else {
    sLElement.innerHTML = '';
    if (!sLIconExists) {
      sLElement.innerHTML = `
        <i onclick="
          change_td_to_input(
            this,
            'partial_exit_${obj_id}',
            'partial_exit_${obj_id}_icon',
            'partial_exit',
            '${obj_id}',
            'partial_exit_${obj_id}'
          )" id="partial_exit_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;">
        </i>`;
    }
    else if (tr_data.partial_exit == null){
      sLIconExists.style.display = 'block';
    }
  }
}

window.update_partial_target = function(obj_id, tr_data){
  const sLElement = document.getElementById(`partial_target_${obj_id}`)
  const sLIconExists = document.getElementById(`partial_target_${obj_id}_icon`);
  if (tr_data.partial_target !== null) {
    sLElement.innerHTML = tr_data.partial_target;
    sLElement.classList.add('change_td_to_input');
    if (sLIconExists) {
      sLIconExists.style.display = 'none'; 
    }
  } else {
    sLElement.innerHTML = '';
    if (!sLIconExists) {
      sLElement.innerHTML = `
        <i onclick="
          change_td_to_input(
            this,
            'partial_target_${obj_id}',
            'partial_target_${obj_id}_icon',
            'partial_target',
            '${obj_id}',
            'partial_target_${obj_id}'
          )" id="partial_target_${obj_id}_icon" class="fas fa-pencil-alt edit-icon" style="cursor: pointer;">
        </i>`;
    }
    else if (tr_data.partial_target == null){
      sLIconExists.style.display = 'block';
    }
  }
}

// --------------------------------------------WEB SOCKET-------------------------------------------

$('#marquee_error').hide();

var ws_scheme = window.location.protocol =="https:" ?"wss" :"ws";
var web_socket_url;
if (location.hostname ==="localhost" || location.hostname ==="127.0.0.1" || location.hostname ==="103.175.23.233" || location.hostname ==="0.0.0.0" || location.hostname ==="103.175.23.233:8040" ) {
    var web_socket_url = window.location.host == '103.175.23.233:8040' ? '103.175.23.233' : window.location.host;
}
else 
{
    var web_socket_url = window.location.host+":8001"
}

let { createApp } = Vue;

let CoinsApp = {data(){return {coin: 'just a coin',coins: null, }},
	created(){

    var user_id = $('#user_id').val();
        // if (!user_id) {
        //     user_id = sessionStorage.getItem('user_id');
        //     if (!user_id) {
        //         window.location.href = "/logout_handler";
        //     }
        // }

		var socket = new ReconnectingWebSocket(`${ws_scheme}://${web_socket_url}/ws/live_socket/`, null, {
      reconnectInterval: 5000,
      maxReconnectAttempts: 20,
    });
    socket.onopen = function() {
        socket.send(JSON.stringify({ 'user_id': user_id }));
        $('#marquee_error').hide();
    };
    socket.onerror = function (error) {
      $('#marquee_error').show();
      console.error('WebSocket error:', error);
    };
		let _this = this; 
		socket.onmessage = function(event)
		{ 
			_this.coins = JSON.parse(event.data);
			if (_this.coins['status'] == 200)
        {
            console.log('Websocket connected...')
            $('#marquee_error').hide();
        }
        else
        {   
        if (_this.coins['live_data']){
					try {
            $('#marquee_error').hide();
            // NIFTY | BANK NIFTY
            let live_data = JSON.parse(_this.coins['live_data'])['26000'];
            let prev_day_close = (live_data && live_data.prev_day_close) ? live_data.prev_day_close : 0;
            let ltp = (live_data && live_data.ltp) ? live_data.ltp : 0;
            let nfty_change = (live_data && live_data.change) ? live_data.change : 0;
        
						let color = (prev_day_close > ltp) ? 'red' : '#00FF00';
						let nf_change = (nfty_change < 0) ? 'red' : '#00FF00';

            if (prev_day_close > ltp){
              $("#nifty_arrow").removeClass( 'fa-solid fa-arrow-up market-arrow')
              $("#nifty_arrow").addClass( 'fa-solid fa-arrow-down market-arrow')
              $("#nifty_arrow").css('color', 'red')
            }
            else{
              $("#nifty_arrow").removeClass( 'fa-solid fa-arrow-up market-arrow')
              $("#nifty_arrow").addClass( 'fa-solid fa-arrow-up market-arrow')
              $("#nifty_arrow").css('color', '#00FF00')
            }
						$('#nifty_ltp').css('color', color); 
						$('#nifty_ltp').html(ltp);     
						$('#nifty_change').css('color', nf_change); 
						$('#nifty_change').html((parseFloat(nfty_change).toFixed(2)))

            // BANK NIFTY
						let bank_nifty_data = JSON.parse(_this.coins['live_data'])['26009']; 
            // let bnf_prev_day_close = bank_nifty_data['prev_day_close'] ? bank_nifty_data['prev_day_close'] : 0;
            let bnf_prev_day_close = (bank_nifty_data && bank_nifty_data.prev_day_close) ? bank_nifty_data.prev_day_close : 0;
            let bnf_ltp = (bank_nifty_data && bank_nifty_data.ltp) ? bank_nifty_data.ltp : 0;
            let bnf_change_val = (bank_nifty_data && bank_nifty_data.change) ? bank_nifty_data.change : 0;
            
						let bn_color = (bnf_prev_day_close > bnf_ltp) ? 'red' : '#00FF00';
            let bnf_change = (bnf_change_val < 0) ? 'red' : '#00FF00';

            if (bnf_prev_day_close > bnf_ltp){ 
              $('#bnf_arrow').removeClass( 'fa-solid fa-arrow-up market-arrow')
              $('#bnf_arrow').addClass( 'fa-solid fa-arrow-down market-arrow')
              $("#bnf_arrow").css('color', 'red')
            }
            else{
              $('#bnf_arrow').removeClass( 'fa-solid fa-arrow-down market-arrow')
              $('#bnf_arrow').addClass( 'fa-solid fa-arrow-up market-arrow')
              $("#bnf_arrow").css('color', '#00FF00')
            }
						$('#bank_nifty').html(bnf_ltp);
						$('#bank_nifty').css('color', bn_color);
						$('#bnf_change').css('color', bnf_change); 
						$('#bnf_change').html((parseFloat(bnf_change_val).toFixed(2)))
            handleLiveData(_this.coins);
					} catch (error) {
						$('#nifty_ltp').html('--');
						$('#bank_nifty').html('--');
						console.log(error)
					}
				}
        var user_id = $('#user_id').val();
        if (!user_id) {
            user_id = sessionStorage.getItem('user_id');
        }
        if (_this.coins['page_update'] && _this.coins['page_update']['instance_data'] && user_id == _this.coins['page_update']['logged_user'] ){
            if (_this.coins['page_update']['instance_data'] && _this.coins['page_update']['index_type'] == 'NIFTY' ) {
               createTableRow(JSON.parse(_this.coins['page_update']['instance_data']) , '#nfty_tbl tbody', 'NIFTY');
                if (_this.coins['page_update']['nifty_open_pos'] && _this.coins['page_update']['nifty_open_pos'] != 0){
                  $("#nifty_open_pos_count").html(_this.coins['page_update']['nifty_open_pos']);
                  $("#nifty_open_pos_count").show()
                }else{
                  $("#nifty_open_pos_count").hide()
                }
            }
            else if (_this.coins['page_update']['instance_data'] && _this.coins['page_update']['index_type'] == 'BANKNIFTY' ){
                createTableRow(JSON.parse(_this.coins['page_update']['instance_data']) , '#nfty_tbl tbody', 'BANKNIFTY');
                if (_this.coins['page_update']['bnf_open_pos'] && _this.coins['page_update']['bnf_open_pos'] != 0){
                  $("#bnf_open_pos_count").html(_this.coins['page_update']['bnf_open_pos']);
                  $("#bnf_open_pos_count").show()
                }
                else{
                  $("#bnf_open_pos_count").hide()
                }
            }
            else if (_this.coins['page_update']['instance_data'] && _this.coins['page_update']['index_type'] == 'EQUITY' ){
                createTableRow(JSON.parse(_this.coins['page_update']['instance_data']) , '#nfty_tbl tbody', 'EQUITY');
                if (_this.coins['page_update']['equity_open_pos'] && _this.coins['page_update']['equity_open_pos'] != 0){
                  $("#equity_open_pos_count").html(_this.coins['page_update']['equity_open_pos']);
                  $("#equity_open_pos_count").show()
                }
                else{
                  $("#equity_open_pos_count").hide()
                }
            }
        }

        if (_this.coins['tr_update']) {
          const tr_data = _this.coins['tr_update'];
          const obj_id = tr_data.tr_id;
          var tr_id = 'tr_' + obj_id;
          const existingRow = document.getElementById(tr_id);
          if (existingRow) {
            update_high_price(obj_id, tr_data)
            update_low_price(obj_id, tr_data)
            update_stoploss_price(obj_id, tr_data)
          }
        }

        // TSL Update
        if (_this.coins['tsl_sl_update']) {
          const tr_data = _this.coins['tsl_sl_update'];
          const obj_id = tr_data.tr_id;
          var tr_id = 'tr_' + obj_id;
          const existingRow = document.getElementById(tr_id);
          if (existingRow) {
            log('---------update stoploss')
            update_stoploss_price(obj_id, tr_data)
          }
        }

        // Full Target Update
        if (_this.coins['target_update']) {
          const tr_data = _this.coins['target_update'];
          const obj_id = tr_data.tr_id;
          var tr_id = 'tr_' + obj_id;
          const existingRow = document.getElementById(tr_id);
          if (existingRow) {
            update_fulltarget(obj_id, tr_data)
            update_stoploss_price(obj_id, tr_data)
            update_order_side(obj_id, tr_data)
          }
        }

        // Hide and Show generate token button
        if (_this.coins['ACCESS_TOKEN_NONE']) {
            const accessToken = _this.coins['ACCESS_TOKEN_NONE'];
            if (accessToken) {
              var activeBtn = document.getElementById('generatetoken_dj');
              if (activeBtn & activeBtn.style.display == 'inline-block') { $("#generatenewtoken").css('display', 'none');  }
              else{ $("#generatenewtoken").css('display', 'block'); }
              $("#generatedtoken").css('display', 'none');
            }
        }

        // Monitor PNL
        if (_this.coins['monitor_pnl']) {
            const pnl_data = JSON.parse(_this.coins['monitor_pnl']);
            Object.keys(pnl_data).forEach(pnl_id => {
                if (pnl_data.hasOwnProperty(pnl_id)) {
                    const element = document.getElementById(pnl_id);
                    if (element) {
                        const pnl_value = pnl_data[pnl_id];
                        const bnf_change = pnl_value < 0 ? 'red' : '#00FF00';
                        element.innerHTML = pnl_value;
                        element.style.cssText = `color: ${bnf_change}; font-weight: bold;`;
                    }
                }
            });
        }

        // Monitor MTM
        if (_this.coins['monitor_mtm']) {
            const mtm_data = JSON.parse(_this.coins['monitor_mtm']);
            Object.keys(mtm_data).forEach(mtm_id => {
              const mtmuserId = mtm_id.split('_')[1];
              if ( user_id == mtmuserId ) {
                if (mtm_data.hasOwnProperty(mtm_id)) {
                    const element = document.getElementById(mtm_id);
                    if (element) {
                        const mtm_value = mtm_data[mtm_id];
                        const mtm_change = mtm_value < 0 ? 'red' : '#00FF00';
                        element.innerHTML = mtm_value.toFixed(2);
                        element.style.cssText = `color: ${mtm_change}; font-weight: bold;`;
                    }
                }
              }
            });
          }

        // CLEAR OVERALL TARGET & SL
        if (_this.coins['overall_tsl_update']) {
          try {
            const tsl_change = JSON.parse(_this.coins['overall_tsl_update']);
            var userId = tsl_change['userId']
            var tradingMode = tsl_change['tradingMode']
            var livesl = tsl_change['live_sl'] == null ? '---' : tsl_change['live_sl']
            var livetarget = tsl_change['live_target'] == null ? '---' : tsl_change['live_target']
            var sl = tsl_change['sl'] == null ? '---' : tsl_change['sl']
            var target =  tsl_change['target'] == null ? '---' : tsl_change['target']  
            var changeTarget = tradingMode == 'Live' ? livetarget : target 
            var changeSl = tradingMode == 'Live' ? livesl : sl
            $(`#profit-value-${userId}`).html(changeTarget)
            $(`#loss-value-${userId}`).html(changeSl)
          } catch (error) {
          }
        }
        
        // CLEAR TR TD FROM TABLE
        if (_this.coins['delete_row_id']) {
          try { document.getElementById(`tr_${_this.coins['delete_row_id']}`).remove();
          } catch (error) {
          }
        }
			}
		}
	}
}
createApp(CoinsApp).mount('#app');


