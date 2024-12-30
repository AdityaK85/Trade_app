import { log, emailValidator,filedValidator, callAjax, fieldsValidator, removeError, resetControls,sweetAlertMsg, showToastMsg } from '../CommonJS/common.js';


window.changeTheme = function(this_){
    if (this_.checked) { 
        document.body.setAttribute('data-layout-mode', 'dark');  
        document.body.setAttribute('data-topbar', 'light');  
    } 
    else {
        document.body.setAttribute('data-layout-mode', 'light');
        document.body.setAttribute('data-topbar', 'dark');  
    } 
}

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var web_socket_url;
if (location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.hostname === "103.175.23.233" || location.hostname === "0.0.0.0" || location.hostname === "103.175.23.233:8040") {
    var web_socket_url = window.location.host == '103.175.23.233:8040' ? '103.175.23.233' : window.location.host;
}
else {
    var web_socket_url = window.location.host + ":8001"
}

let { createApp } = Vue;

let CoinsApp = {
    data() { return { coin: 'just a coin', coins: null, } },
    created() {
        var socket = new ReconnectingWebSocket(`${ws_scheme}://${web_socket_url}/ws/live_socket/`, null, {
            reconnectInterval: 5000,
            maxReconnectAttempts: 20,
        });
        socket.onopen = function () {
            socket.send(JSON.stringify({ 'user_id': 0 }));
            $('#marquee_error').hide();
        };
        socket.onerror = function (error) {
            console.error('WebSocket error:', error);
        };
        let _this = this;
        socket.onmessage = function (event) {
            _this.coins = JSON.parse(event.data);
            if (_this.coins['status'] == 200) {
                console.log('Screener Websocket connected...')
            }
            else {

                if (_this.coins['live_data']  ) {

                    try {

                        
                        let live_data = JSON.parse(_this.coins['live_data']);
                        Object.keys(live_data).forEach((key) => {
                            
                            let data = live_data[key];
                            let element = document.getElementById(key);
                            let change_ele = document.getElementById(`${key}_change`);
                            let feed_ele = document.getElementById(`${key}_feed_div`);
                            let arrow_ele = document.getElementById(`${key}_arrow`);

                            if (element) {
                                element.innerHTML = data.ltp;
                                if (data.market_status) {
                                    const change_perc = data.change_perc;
                                    if (change_ele) change_ele.innerHTML = change_perc;
                                
                                    if (feed_ele) {
                                        const isPositive = change_perc > 0;
                                        feed_ele.style.color = isPositive ? '#33b888' : 'red';
                                        feed_ele.style.fontWeight = '700';
                                        if (arrow_ele) arrow_ele.innerHTML = isPositive ? '▲' : '▼';
                                    }
                                } else {
                                    $(".market-change").css('display', 'none')
                                    $("#timing").html(data.time)
                                }
                            }
                        });
                        handleLiveData(_this.coins);
                    } catch (error) {
                        console.error(error)   
                    }
                }

                if (_this.coins['page_update']) {
                    const page_update = _this.coins['page_update'];
                    log(page_update)
                    $("#position-tables").html(page_update);
                }

                if (_this.coins['monitor_pnl']) {
                    const pnl_data = JSON.parse(_this.coins['monitor_pnl']);
                    Object.keys(pnl_data).forEach(pnl_id => {
                        if (pnl_data.hasOwnProperty(pnl_id)) {
                            const element = document.getElementById(pnl_id);
                            if (element) {
                                const pnl_value = pnl_data[pnl_id];
                                const bnf_change = pnl_value < 0 ? 'red' : '#34c38f';
                                element.innerHTML = pnl_value;
                                element.style.cssText = `color: ${bnf_change}; font-weight: bold;`;
                            }
                        }
                    });
                }

                if (_this.coins['monitor_mtm']) {
                    const mtm_data = JSON.parse(_this.coins['monitor_mtm']);
                    Object.keys(mtm_data).forEach(mtm_id => {
                        if (mtm_data.hasOwnProperty(mtm_id)) {
                            const element = document.getElementById(mtm_id);
                            if (element) {
                                const mtm_value = mtm_data[mtm_id];
                                const mtm_change = mtm_value < 0 ? 'red' : '#34c38f';
                                element.innerHTML = mtm_value.toFixed(2);
                                element.style.cssText = `color: ${mtm_change}; font-weight: bold;`;
                            }
                        }
                    });
                  }
                
            }
        }
    }
}
createApp(CoinsApp).mount('#app');



// Banknifty 
// https://priceapi.moneycontrol.com/pricefeed/notapplicable/inidicesindia/in%3Bnbx

// Nifty 
// https://priceapi.moneycontrol.com/pricefeed/notapplicable/inidicesindia/in%3BNSX

// https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/history?symbol=ICICIBANK&resolution=1D&from=1735036930&to=1735036553&countback=2&currencyCode=INR