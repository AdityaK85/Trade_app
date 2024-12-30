import { log, emailValidator,filedValidator, callAjax, fieldsValidator, removeError, resetControls,sweetAlertMsg, showToastMsg } from '../CommonJS/common.js';

window.removeError = removeError

$('#dashboard_div').addClass("mm-active");
$('#limitPriceField').hide();


window.toggleLimitPriceField = function(this_){
    if (this_.value == 'Market') $('#limitPriceField').hide();
    else  $('#limitPriceField').show();
}

window.orderExecutionCard = function(status){
    if (status == 'show') $('#order_excution_card').show();
    else  $('#order_excution_card').hide();
}

window.NIFTY_STRIKE_TOKENS = [];
window.BANKNIFTY_STRIKE_TOKENS = [];

window.showSelected_Strike = function(selectedStrikePrice, changeIndex) {
    let $dropdown = $(`#strike_price`);
    $dropdown.val(selectedStrikePrice);
    if (!$dropdown.find(`option[value="${selectedStrikePrice}"]`).length) {
        $dropdown.append(`<option value="${selectedStrikePrice}">${selectedStrikePrice}</option>`);
        $dropdown.val(selectedStrikePrice);
    }
    $dropdown.trigger('change');
}

window.populateStrikePrices = function(strikes = [], index = null, showLoader = false, set_selected_strike = null) {
    let changeIndex = (index == 'NIFTY') ? 'nfty' : 'bnf';
    const select = document.getElementById(`strike_price`);

    if (showLoader) {
        select.innerHTML = '<option value="" disabled selected>Loading...</option>';
    } else {
        const options = ['<option value="" disabled selected>Select Strike Price</option>']
            .concat(strikes.map(item => `<option value="${item}">${item}</option>`))
            .join('');
        select.innerHTML = options;
        showSelected_Strike(set_selected_strike, changeIndex);
    }
};



window.getStrikePrice = async function(index) {
    populateStrikePrices([], index, true, null);
    try {
        const response = await callAjax('/get_strike_price/', { 'index': index });
        if (response.status === 1) {
            populateStrikePrices(response.unique_strikes, index, false, response.show_selected_strike);
            if (index === 'NIFTY')  NIFTY_STRIKE_TOKENS = response.update_unique_dict;
            else BANKNIFTY_STRIKE_TOKENS = response.update_unique_dict;
        } else showToastMsg('Error', 'Failed to load strike prices', 'error');
    } catch (error) {
        showToastMsg('Error', 'An error occurred while fetching strike prices', 'error');
    }
};

window.activateBreakout = function (index) {
    if (index != 'equity') { $(`#${index}_strikeprice_div`).css('display', 'none'); $(`#${index}_strikeroundup_div`).css('display', 'block'); $(`#${index}_breakouthighlow_div`).css('display', 'block'); }
    else { $(`#${index}_strikeroundup_div`).css('display', 'none'); $(`#${index}_breakouthighlow_div`).css('display', 'block'); } 
    $(`#${index}_executeon_div`).css('display', 'none');
    $(`#${index}_breakoutcandle_div`).css('display', 'block');
    $(`#${index}_timeframe_div`).css('display', 'block');
    $(`#${index}_option_div`).css('display', 'none');
    $(`#${index}_limitprice_div`).css('display', 'none');
    $(`#${index}_breakout_lable`).addClass("active");
    $(`#${index}_strikeprice_lable`).removeClass("active");
}

window.activateStrikePrice = function (index) {
    $(`#${index}_breakoutcandle_div`).css('display', 'none');
    $(`#${index}_timeframe_div`).css('display', 'none');
    $(`#${index}_strikeprice_div`).css('display', 'block');
    $(`#${index}_executeon_div`).css('display', 'block');
    $(`#${index}_limitprice_div`).css('display', 'none');
    $(`#${index}_strikeprice_lable`).addClass("active");
    $(`#${index}_breakout_lable`).removeClass("active");
    if (index != 'equity') { $(`#${index}_strikeroundup_div`).css('display', 'none'); getStrikePrice(index); $(`#${index}_option_div`).css('display', 'block'); $(`#${index}_breakouthighlow_div`).css('display', 'none');}
    else {
        $(`#${index}_option_div`).css('display', 'none');
        $(`#${index}_breakouthighlow_div`).css('display', 'none');
    } 
}

getStrikePrice($("#indexSelect").val())
// document.addEventListener("DOMContentLoaded", function () {
//     const breakoutRadio = document.getElementById("vbtn-indexSelect");
//     breakoutRadio.checked = true;
//     breakoutRadio.click();
// });

// document.addEventListener("DOMContentLoaded", function () {
//     const bnf_breakoutRadio = document.getElementById("bnf-vbtn-radio4");
//     bnf_breakoutRadio.checked = true;
//     bnf_breakoutRadio.click();
// });

// document.addEventListener("DOMContentLoaded", function () {
//     const equity_breakoutRadio = document.getElementById("equity-vbtn-radio4");
//     equity_breakoutRadio.checked = true;
//     equity_breakoutRadio.click();
// });

window.executeon = function (selected, index) {
    if (selected === 'Breakout') {
        $(`#${index}_breakoutcandle_div`).css('display', 'block');
        $(`#${index}_timeframe_div`).css('display', 'block');
        $(`#${index}_limitprice_div`).css('display', 'none');
        if (index == 'equity') { $(`#${index}_breakouthighlow_div`).css('display', 'block'); } 
        
    } else if (selected === 'Limit') {
        $(`#${index}_limitprice_div`).css('display', 'block');
        $(`#${index}_breakoutcandle_div`).css('display', 'none');
        $(`#${index}_timeframe_div`).css('display', 'none');
        $(`#${index}_breakouthighlow_div`).css('display', 'none');
        
    } else {
        $(`#${index}_limitprice_div`).css('display', 'none');
        $(`#${index}_breakoutcandle_div`).css('display', 'none');
        $(`#${index}_timeframe_div`).css('display', 'none');
        $(`#${index}_breakouthighlow_div`).css('display', 'none');
    }
}

// document.addEventListener("DOMContentLoaded", function () {
//     const changeSelector = document.getElementById('vbtn-radio1');
//     changeSelector.addEventListener("input", function () {
//         const marketRadio = document.getElementById("vbtn-radio5");
//         if (marketRadio) {
//             marketRadio.checked = true;
//             marketRadio.click();
//         }
//     });
// });

// document.addEventListener("DOMContentLoaded", function () {
//     const bnfchangeSelector = document.getElementById('bnf-vbtn-radio1');
//     bnfchangeSelector.addEventListener("input", function () {
//         const bnfmarketRadio = document.getElementById("bnf-vbtn-radio5");
//         if (bnfmarketRadio) {
//             bnfmarketRadio.checked = true;
//             bnfmarketRadio.click();
//         }
//     });
// });

// document.addEventListener("DOMContentLoaded", function () {
//     const equitychangeSelector = document.getElementById('equity-vbtn-radio1');
//     equitychangeSelector.addEventListener("input", function () {
//         const equitymarketRadio = document.getElementById("equity-vbtn-radio5");
//         if (equitymarketRadio) {
//             equitymarketRadio.checked = true;
//             equitymarketRadio.click();
//         }
//     });
// });


window.increase_strike_round_up = function(input_id, event, Indice) {
    event.preventDefault();
    let inputField = document.getElementById(input_id);
    let currentValue = parseInt(inputField.value, 10);
    if (isNaN(currentValue)) currentValue = 0;
    var checkRoundup = (Indice == 'BANKNIFTY') ? 500 : 500;
    if (currentValue < checkRoundup) {
        inputField.value = currentValue + 100 > 500 ? 500 : currentValue + 100;
    }
}

window.decrease_strike_round_up = function(input_id, event , Indice) {
    event.preventDefault();
    let inputField = document.getElementById(input_id);
    let currentValue = parseInt(inputField.value, 10);
    if (isNaN(currentValue)) currentValue = 0;
    var checkRoundup = (Indice == 'BANKNIFTY') ? 500 : 500;
    if (currentValue > -checkRoundup) {
        inputField.value = currentValue - 100 < -500 ? -500 : currentValue - 100;
    }
}



window.clear_nfty_values = function(){
    $("#nfty_lot_size").val('')
    $("#nfty_breakout_candle").val('')
    $("#nfty_timeframe").val('')
    $("#nfty_breakout_on").val('')
    $("#nfty_strikeRoundUp").val('0')
    $('#nfty_timeframe').prop('selectedIndex', 0);
    $('#nfty_breakout_on').prop('selectedIndex', 0);
}

window.clear_bnf_values = function(){
    $("#bnf_lot_size").val('')
    $("#bnf_breakout_candle").val('')
    $("#bnf_timeframe").val('')
    $("#bnf_breakout_on").val('')
    $("#bnf_strikeRoundUp").val('0')
    $('#bnf_timeframe').prop('selectedIndex', 0);
    $('#bnf_breakout_on').prop('selectedIndex', 0);
}

window.clear_equity_values = function(){
    $("#equity_lot_size").val('')
    $("#equity_limit_price").val('')
    $("#equity_breakout_candle").val('')
    $("#equity_timeframe").val('')
    $('#equity_timeframe').prop('selectedIndex', 0);
}

window.SaveBreakoutStretegy = async function(_this ) {
    
    try {
        var indexselect = $("#indexSelect").val() 
        var strike_price = $("#strike_price").val()
        var option_type = $("#option_type").val()
        var lotSize = $("#lotSize").val()
        var orderSide = $("#orderSide").val()
        var priceType = $("#priceType").val()
        var limitPrice = $("#limitPrice").val()
        var stopLoss = $("#stopLoss").val()
        var target = $("#target").val()

        if (strike_price == "") {
            $("#strike_price").addClass("error_class");
            $("#strike_price").focus();
            return false;
        }
        else if (lotSize.trim() == "") {
            $("#lotSize").addClass("error_class");
            $("#lotSize").focus();
            return false;
        }
        else if (priceType == 'Limit' && limitPrice.trim() == "" ) {
            $("#limitPrice").addClass("error_class");
            $("#limitPrice").focus();
            return false;
        }
        else {

                var get_data = {
                    'indexselect': indexselect,
                    'strike_price': strike_price,
                    'option_type': option_type,
                    'lotSize': lotSize,
                    'orderSide': orderSide,
                    'priceType': priceType,
                    'limitPrice': limitPrice,
                    'stopLoss': stopLoss,
                    'target': target,
                }

                var response = await callAjax('/save-stretegy/', get_data , _this, 'Executing', 'Execute');
                if (response.status == 1) {
                    // await clear_nfty_values()
                    // await clear_bnf_values()
                    // await clear_equity_values()
                    $("#position-tables").html(response.pos_string);
                }
                else if (response.status == 2) {
                        sweetAlertMsg('Candle Not Found', response.msg, 'warning')
                }
            }    
        } catch (error) {
        sweetAlertMsg('Something went wrong', 'There is a problem please try again', 'warning')
        console.log(error)
    }
}


window.getRandomNumber = function(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


window.updateLiveLtp_ForStrikePrice = function (index, live_data) {
    // log(index, NIFTY_STRIKE_TOKENS)
    const niftystrikeEle = document.getElementById(`strike_price`);
    const niftyOptionEle = document.getElementById(`option_type`);
    if (!niftystrikeEle || !niftystrikeEle.options || niftystrikeEle.selectedIndex < 0) {
        console.error("Invalid or missing strike price element for index:", index);
        $(`#strike_ltp`).text('---');
        return;
    }
    const strikePrice = niftystrikeEle.options[niftystrikeEle.selectedIndex]?.text || '---';
    const useFeed = (index == 'NIFTY') ? window.NIFTY_STRIKE_TOKENS : window.BANKNIFTY_STRIKE_TOKENS;
    const loader = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'
    const ltpElement = $(`#strike_ltp`);
    if (niftystrikeEle.value != ""){ ltpElement.html(loader);}
    if ( niftyOptionEle && niftyOptionEle.value != ""){
        const optType = niftyOptionEle.value;
        const updatedStrike = strikePrice+optType;
        const getDataDict = useFeed.find(item => item.new_strike == updatedStrike);
        if (getDataDict && getDataDict != null && getDataDict != undefined) {
            Object.keys(live_data).forEach(token => {
                ltpElement.html(loader);
                if (live_data[getDataDict.token] && live_data[getDataDict.token].ltp !== undefined) {
                    const ltpValue = live_data[getDataDict.token].ltp;
                    ltpElement.html(loader);
                    $(`#strike_ltp`).text(ltpValue);
                }
            });
        }
    }
    else  $(`#strike_ltp`).text('---');
}

window.updateLiveLtp_ForEQStocks = function (index, live_data) {
    const equityStocksEle = document.getElementById(`${index}_strike_price`);
    if (!equityStocksEle || !equityStocksEle.options || equityStocksEle.selectedIndex < 0) {
        $(`#${index}_strike_ltp`).text('---');
        return;
    }
    const loader = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'
    const ltpElement = $(`#${index}_strike_ltp`);
    if (equityStocksEle.value == ""){ return ltpElement.html(loader); }
    var eq_toke = parseInt(equityStocksEle.value)
    Object.keys(live_data).forEach(token => {
        ltpElement.html(loader);
        if (live_data[eq_toke] && live_data[eq_toke].ltp !== undefined) {
            const ltpValue = live_data[eq_toke].ltp;
            ltpElement.html(loader);
            $(`#${index}_strike_ltp`).text(ltpValue);
        }
    });
}

window.handleLiveData = function (live_data_web) {
    const live_data = JSON.parse(live_data_web['live_data']);
    const classToElementsMap = {};
    Object.keys(live_data).forEach(token => {
        const classes = [`nfty_${token}_ltp`, `bnf_${token}_ltp`];
        classes.forEach(td_class => {
            if (!classToElementsMap[td_class]) {
                classToElementsMap[td_class] = Array.from(document.getElementsByClassName(td_class));
            }
        });
    });
    Object.keys(live_data).forEach(token => {
        const ltpValue = live_data[token].ltp;
        const classes = [`nfty_${token}_ltp`, `bnf_${token}_ltp` , `equity_${token}_ltp`];
        classes.forEach(td_class => {
            const elements = classToElementsMap[td_class] || [];
            elements.forEach(element => {
                element.innerHTML = ltpValue;
            });
        });
    });
    updateLiveLtp_ForStrikePrice($("#indexSelect").val() , live_data)
}


window.save_target_sl_other_setup = async function(pos_id , value,  type, icon_id){
    var response = await callAjax('/save-target-sl-other-setup/', {'id':pos_id , 'value':value , 'type':type})
    if (response.status == 1)
    {   
        if (response.send_on_front == null || response.send_on_front == ""){
            $(`#${icon_id}`).css('display', 'block');
        }
    }
    else showToastMsg('Error', response.msg, 'error')
    
}

window.save_target = async function(user_id, target_input){
    var tp = $(`#${target_input}`).val();
    var response = await callAjax('/save-target-points/', {'user_id':user_id , 'target_input':tp, 'index' : target_input})
    if (response.status == 1) showToastMsg('Success', response.msg, 'success')
    else showToastMsg('Error', response.msg, 'error')
}

window.refreh_tbl = async function(user_id){
    var response = await callAjax('/refresh_index/', {'user_id':user_id})
    if (response.status == 1) {
        $("#nifty_positions_container").html(response.nifty_string);
        $("#bnf_positions_container").html(response.bnf_string);
        $("#equity_positions_container").html(response.eq_rendered);
    } 
    else showToastMsg('Error', 'Something went wrong ', 'error')
}



$(document).on('click', '.change_td_to_input', function() {
    var tdId = $(this).data('id');
    var type = $(this).data('type');
    var td_id = `${type}_${tdId}`;
    var icon_id = `${type}_${tdId}_icon`;
    var lot_size_id = `lot_size_${tdId}`;
    change_td_to_input(this, td_id, icon_id, type, tdId, lot_size_id);
    $(this).removeClass('change_td_to_input');
});


window.change_td_to_input = async function(this_,   td_id, icon_id, change_type, pos_id, lot_size_id) {
    var lot_size = $(`#${lot_size_id}`).text().trim();
    var currentText = $(`#${td_id}`).text().trim();
    var inputField = $('<input>', {
        type: 'text',
        id: `edit_input_${td_id}`,
        name: `edit_input_${td_id}`,
        class: 'form-control form-control-sm',
        style: 'min-width: 60px;',
        value: currentText,
        autocomplete: 'off'
    }).on('input', function() {
        var value = $(this).val();
        try {
            let textPart = this.id.match(/^[^\d]+/)[0];
            if (textPart == 'edit_input_partial_exit_') {
                $(this).val(value.replace(/\D/g, ''));
            }
            else {
                if (!/^\d*\.?\d*$/.test(value)) {
                    $(this).val(value.replace(/[^0-9.]/g, ''));
                }
                if ((value.match(/\./g) || []).length > 1) {
                    $(this).val(value.slice(0, -1));
                }
            }
        } catch (error) {   
            if (!/^\d*\.?\d*$/.test(value)) {
                $(this).val(value.replace(/[^0-9.]/g, ''));
            }
            if ((value.match(/\./g) || []).length > 1) {
                $(this).val(value.slice(0, -1));
            }
        }

    });
    var saveButton = $('<button>', {
        id: `save_button_${td_id}`,
        class: 'mx-1 btn btn-sm btn-primary',
        html: '<i class="fas fa-save"></i>',
        style: 'cursor: pointer;width: auto;',
        type: 'button'
    });

    try {
        $(`#${icon_id}`).css('display', 'none');
    } catch (error) {
        
    }
    $(`#${td_id}`).html(inputField).append(saveButton);
        $(`#save_button_${td_id}`).on('click', function() {
            var newValue = $(`#edit_input_${td_id}`).val();

            let newValueInt = newValue !== "" ? parseInt(newValue) : 0;
            let lot_sizeInt = parseInt(lot_size);

            if (change_type == 'partial_exit' && (lot_sizeInt <= newValueInt  ||  newValueInt == 0  ) && newValueInt != ""  ){
                showToastMsg('Error', 'Partial lot size should be less than total lot size ', 'error')
            }
            else{
                save_target_sl_other_setup(pos_id, newValue,  change_type, icon_id)
                $(`#${td_id}`).html(newValue);
                $(`#${td_id}`).addClass('change_td_to_input');
            }
        });
        $(`#edit_input_${td_id}`).on('keypress', function(event) {
            if (event.which === 13) {
                event.preventDefault();
                var newValue = $(`#edit_input_${td_id}`).val();
                let newValueInt = newValue !== "" ? parseInt(newValue) : 0;
                let lot_sizeInt = parseInt(lot_size);
                if (change_type == 'partial_exit' && (lot_sizeInt <= newValueInt || newValueInt == 0) && newValueInt !== "") {
                    showToastMsg('Error', 'Partial lot size should be less than total lot size', 'error');
                } else {
                    save_target_sl_other_setup(pos_id, newValue, change_type, icon_id);
                    $(`#${td_id}`).html(newValue);
                    $(`#${td_id}`).addClass('change_td_to_input');
                }
            }
        });

        $(`#edit_input_${td_id}`).focus();
}


window.square_off_pos = async function(pos_id, trade_mode ,  this_ ){
    var response = await callAjax('/square_off_position/', {'pos_id':pos_id , 'trade_mode':trade_mode} , this_ , '', '<i class="fa-solid fa-arrow-right-from-bracket"></i>' )
    if (response.status == 1){
        await showToastMsg('Success', response.msg, 'success')
    }
    else{
        await sweetAlertMsg('Error', 'Something went wrong', 'error')
    }
}

window.delete_pos = async function(pos_id, trade_mode ,  this_ ){

    var pref = await sweetAlertMsg(`Delete Position`, `Do you want to delete this position?`, 'question', 'cancel', 'Yes', )
    if (pref){
        var response = await callAjax('/delete_position/', {'pos_id':pos_id , 'trade_mode':trade_mode} , this_ , '', '<i class="fa-solid fa-xmark"></i>' )
        if (response.status == 1){
            $("#position-tables").html(response.nft_rendered);
            await showToastMsg('Success', response.msg, 'success')
        }
        else{
            await sweetAlertMsg('Error', 'Something went wrong', 'error')
        }
    }
}