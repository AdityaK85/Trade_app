from datetime import datetime as dt , date, timedelta
import time
from django.conf import settings
import requests, random, traceback
import calendar
from asgiref.sync import async_to_sync
from algosee_app.models import *
from connections.order_utility import CreateLiveOrder, SaveOrder, order_monitoring

today = date.today()

def getRealizedMTM(buyAvg, sellAvg, Qty, cfQty):
	quantity = int(Qty) + int(cfQty)
	return round((float(sellAvg) - float(buyAvg)) * quantity, 2)

def get_instrument_token(buy_symbol  ):
    try:
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/search?key={buy_symbol}'
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.request("GET", url, headers=headers)
        json_response = response.json() 
        if 'result' in json_response:
            try:
                if json_response['result']:
                    return json_response['result'][0]['token'], json_response['result'][0]['symbol']
                else:
                    None, None
            except:
                traceback.print_exc()
                return None, None
        else:
            return None, None
    except:
        print(str(traceback.format_exc()))
    return None

# BANKNIFTY24N0651900CE  -- this for weekly expiry
# BANKNIFTY24NOV51900CE  -- this for monthly expiry

def new_generate_symbol(expiry_date, symbol, strike_price, option_type):
    year = expiry_date.strftime('%y')
    day = expiry_date.strftime('%d')
    month = expiry_date.strftime('%b')[0]
    token = None
    if is_last_week_of_month(expiry_date) or symbol == 'BANKNIFTY':
        month = expiry_date.strftime('%b').upper()
        token = f'{symbol}{year}{month}{strike_price}{option_type}'
    else:
        token = f'{symbol}{year}{month}{day}{strike_price}{option_type}'
    return token

def is_last_week_of_month(ex_date):
    last_day = calendar.monthrange(ex_date.year, ex_date.month)[1]
    return (last_day - ex_date.day) < 7

########## get instrument token
def getTurboSymbolToken(symbol, strike, opt_type, exp_date):
    try:
        symbol = symbol.upper()
        symb_date = OptionExpiry.objects.filter(index=symbol).order_by('expiry').first()
        if not symb_date:
            return None, None
        expiry_date = symb_date.expiry
        return_token = new_generate_symbol(expiry_date, symbol, strike, opt_type)
        get_symbol = SymbolsMaster.objects.filter(trading_symbol=return_token).last()
        if get_symbol:
            return get_symbol.token, get_symbol.trading_symbol
        else:
            instrument_token, tradingSymbol = get_instrument_token(return_token)
            return instrument_token, tradingSymbol
    except Exception:
        traceback.print_exc()
        return None

import requests
import pandas as pd


def update_bnf_expiry():
    try:
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'application/json',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        OptionExpiry.objects.filter(index="BANKNIFTY").delete()
        with requests.Session() as session:
            response = session.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            expiry_dates = data['records']['expiryDates']
            for expiry_str in expiry_dates:
                expiry_date = dt.strptime(expiry_str, '%d-%b-%Y').date()
                if not OptionExpiry.objects.filter(index="BANKNIFTY", expiry=expiry_date).exists():
                    option_expiry = OptionExpiry(index="BANKNIFTY", expiry=expiry_date)
                    option_expiry.save()
            return True

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def update_nifty_expiry():
    try:
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'application/json',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        OptionExpiry.objects.filter(index="NIFTY").delete()
        with requests.Session() as session:
            response = session.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            expiry_dates = data['records']['expiryDates']
            for expiry_str in expiry_dates:
                expiry_date = dt.strptime(expiry_str, '%d-%b-%Y').date()
                if not OptionExpiry.objects.filter(index="NIFTY", expiry=expiry_date).exists():
                    option_expiry = OptionExpiry(index="NIFTY", expiry=expiry_date)
                    option_expiry.save()
            return True
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.initialize_mastertrust_data()
        return cls._instance

    def initialize_mastertrust_data(self):
        try:
            url = 'https://masterswift.mastertrust.co.in/api/v2/contracts.json?exchanges=NFO'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            nse_opt_data = data.get("NSE-OPT", [])
            self.token_df = pd.DataFrame.from_dict(nse_opt_data)
            self.token_df['expiry'] = pd.to_datetime(self.token_df['expiry'], unit='s')
            self.token_df = self.token_df.dropna(subset=['expiry'])
            self.tokens_dict = {}
            for _, row in self.token_df.iterrows():
                token_data = { 
                    'token': row['code'],  
                    'symbol': row['symbol'], 
                    'expiry': row['expiry'],
                    'exchange_code': row['exchange_code']
                }
                self.tokens_dict[row['code']] = token_data
        except:
            ErrorLog.objects.create(error=traceback.format_exc())
    
    def get_exchange_code_by_token(self, token, full_data = True):
        token_data = self.tokens_dict.get(token)
        if token_data and full_data == False :
            return token_data['exchange_code']
        return token_data

    def get_data(self):
        return { "tokens_dict": self.tokens_dict }
############################################# Turbo trade order history
def orderHistory(client_id, access_token, oms_order_id):
    url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/order/{oms_order_id}/history?client_id={client_id}'
    headers = {
        'x-device-type': 'WEB',
        'client_id': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.request("GET", url, headers=headers, data={})
    response = response.json()
    order_obj = Orders.objects.filter(oms_order_id = oms_order_id).last()
    if ('status' in response and response['status'] != 'error'):
        oms_order_details = None
        try:
            oms_order_details = response['data'][0]
        except:
            pass
        if oms_order_details:
            if oms_order_details['status'] != 'rejected':
                return response
            else:
                return response 
        else:
            return response
    else:
        return response
############################################# get order history
def getOrderBookMonitoring(broker, orderSide, trading_symbol):
    try:
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/orders?type=all&client_id={broker.client_id}'
        headers = {
            'x-device-type': 'WEB',
            'client_id': broker.client_id,
            'Authorization': f'Bearer {broker.access_token}'
        }
        response = requests.request("GET", url, headers=headers, data={})
        sorted_data = sorted(response.json()['data']['orders'], key=lambda item: int(item['order_entry_time']), reverse=True)
        try:
            orderBookOrders = [orderBookOrder for orderBookOrder in sorted_data if orderBookOrder['order_side'] == orderSide and orderBookOrder['trading_symbol'] == trading_symbol]
            latestOrder = max(orderBookOrders, key=lambda order: order['order_entry_time'])
            return float(latestOrder['average_trade_price'])
        except:
            return None
    except:
        traceback.print_exc()
    return []


def placeOrder(data, broker):
    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        order_id = random.randrange(1, 10 ** 30)
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/orders?disclosed_quantity=0&exchange={data.get("exchange")}&instrument_token={data.get("token")}&market_protection_percentage=0&order_side={data.get("orderSide")}&order_type=MARKET&price=0&product={data.get("product")}&quantity={abs(data.get("quantity")) }&trigger_price=0&validity=DAY&user_order_id={order_id}&client_id={broker.client_id}'
        headers = {
            'x-device-type': 'WEB',
            'client_id': broker.client_id,
            'Authorization': f'Bearer {broker.access_token}'
        }
        response = requests.request("POST", url, headers=headers, data={})
        response = response.json()
        fk_pos_obj = BreakoutPosition.objects.filter(id = data.get('strategy')).last()
        ResponseLog.objects.create(response = f' PLACE  ORDER  FUNCTION CALLED RESPONSE ===url {url}====response=== {response}')
        print(':: TURBO TRADE ORDER :: RESPONSE :: ', response, ' ::', response.get('status'))
        clearAccessToken = False
        if response:
            order_obj = CreateLiveOrder( data.get('strategy'), data.get('ltp') , abs(data.get("quantity") )  if data.get("quantity") != None else data.get("quantity") ,  order_id, data.get("exchange"), data.get("token"), data.get("orderSide"), data.get("orderType"), data.get("product"),  'Live' , data.get("symbol"), None, 'Pending' , None )

            if 'status' in response and response['status'] != 'error':    
                try:
                    # time.sleep(2)
                    oms_order_id = response['data'].get('oms_order_id')  
                    order_obj.oms_order_id = oms_order_id
                    order_obj.remark = response['message']
                    order_obj.save()

                    datalst = getPositions(broker.client_id, broker.access_token)
                    dataList = datalst.get('data')
                    order_resp = orderHistory(broker.client_id, broker.access_token , oms_order_id)

                    try:
                        if order_resp['data'][0]['status'] == "complete":
                            order_obj.status = 'OPEN'
                            order_obj.save()
                            position_dict = [item for item in dataList if item.get('token') == int(data.get("token"))]
                            Request = {"client_id":broker.client_id, "access_token": broker.access_token, "oms_order_id":response['data']['oms_order_id']}
                            ResponseLog.objects.create(response = f' PLACE  ORDER  FUNCTION CALLED RESPONSE ===Request body {Request}====response=== {order_resp} ============position response============{position_dict}')
                            orderSide = order_resp['data'][0]['order_side']
                            if position_dict:
                                if orderSide == order_obj.order_side:
                                    order_obj.entryPrice = order_resp['data'][0]['avg_price']
                                    order_obj.ltp = position_dict[0]['ltp']
                                    order_obj.buyAvg = order_resp['data'][0]['avg_price']
                                    order_obj.buyQty = position_dict[0]['buy_quantity']
                                    order_obj.qty = position_dict[0]['net_quantity']
                                    order_obj.save()

                        elif order_resp['data'][0]['status'] == 'rejected':
                            order_obj.fk_strategy.pos_status = 'REJECTED'
                            order_obj.status = 'CLOSED'
                            order_obj.fk_strategy.pos_remark = 'Order has been rejected'
                            order_obj.remark = order_resp['data'][0]['reject_reason']
                            order_obj.save()
                            order_obj.fk_strategy.save()

                        elif 'status' in order_resp and order_resp['status'] == 'error':
                            order_obj.fk_strategy.pos_status = 'REJECTED'
                            order_obj.status = 'CLOSED'
                            order_obj.fk_strategy.pos_remark = 'Order has been rejected'
                            order_obj.remark = "Order Rejected! Please try again"
                            order_obj.save()
                            order_obj.fk_strategy.save()

                            ResponseLog.objects.create(response = f' PLACE  ORDER REJECTEC RESPONSE ====response=== {order_resp}')
                            print(':: ORDER FAILED :: USER :: BROKER :: MASTERTRUST :: RESPONSE :: ', response)
                    except:
                        order_obj.fk_strategy.pos_status = 'REJECTED'
                        order_obj.status = 'CLOSED'
                        order_obj.fk_strategy.pos_remark = 'Order has been rejected'
                        order_obj.remark = "Order Rejected! Please try again"
                        order_obj.save()
                        order_obj.fk_strategy.save()
                        ErrorLog.objects.create(error=traceback.format_exc())
                        traceback.print_exc()
                except:
                    order_obj.fk_strategy.pos_status = 'REJECTED'
                    order_obj.status = 'CLOSED'
                    order_obj.fk_strategy.pos_remark = 'Order has been rejected'
                    order_obj.remark = "Order Rejected! Please try again"
                    order_obj.save()
                    order_obj.fk_strategy.save()
                    ErrorLog.objects.create(error=traceback.format_exc())
                    traceback.print_exc()
                print(':: ORDER PLACED :: USER :: BROKER :: MASTERTRUST :: RESPONSE :: ', response)
            else:
                print(':: ORDER FAILED :: USER :: BROKER :: MASTERTRUST :: RESPONSE :: ', response)
                fk_pos_obj.pos_remark = response.get('message') if 'message' in response else 'Order Rejected'
                order_obj.remark = "Something went wrong! Please regenerate token and try again"
                fk_pos_obj.pos_status = 'ERROR'
                order_obj.status = 'ERROR'
                broker.access_token = None
                broker.is_login = False
                broker.save()
                order_obj.save()
                fk_pos_obj.save()
                clearAccessToken = True
        else:
            fk_pos_obj.pos_remark = response.get('message') if 'message' in response else 'Order Failed'
            order_obj.remark = "Something went wrong! Please regenerate token and try again"
            fk_pos_obj.pos_status = 'ERROR'
            order_obj.status = 'ERROR'
            broker.access_token = None
            broker.save()
            broker.is_login = False
            order_obj.save()
            fk_pos_obj.save()
            clearAccessToken = True
        
        if clearAccessToken:
            async_to_sync(channel_layer.group_send)(
                    "Test_Consumer",
                    {
                        "type": "send_live_data",
                        "value": {'ACCESS_TOKEN_NONE': True  }
                    }
                ) 
    except:
        ErrorLog.objects.create(error=traceback.format_exc())
        traceback.print_exc()
    return False

'''
{'data': {'client_order_id': '24010900040316', 'oms_order_id': '24010900040316', 'user_order_id': 920808765576398721235290055656}, 'message': 'Order place successfully', 'status': 'success'} 
'''

def PlacePaperOrder(data):
    try:
        order_id = random.randrange(1, 10 ** 30)
        exchange = data.get('exchange')
        token = data.get('token')
        orderSide = data.get('orderSide')
        orderType = data.get('orderType')
        product = data.get('product')
        quantity = abs(data.get('quantity')) 
        symbol = data.get('symbol')
        order_mode = data.get('order_mode')
        strategy = data.get('strategy')
        ltp = data.get('ltp')
        SaveOrder(strategy, ltp, quantity,  order_id, exchange, token, orderSide, orderType, product,  order_mode , symbol)
        return True
    except:
        traceback.print_exc()



######################################## square of position
def squareOffPosition(position, quantity, broker, remark):
    try:
        order_id = random.randrange(1, 10 ** 30)
        order_side = 'SELL' if position.order_side == 'BUY' else 'BUY'

        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/orders?disclosed_quantity=0&exchange={position.exchange}&instrument_token={position.token}&market_protection_percentage=0&order_side={order_side}&order_type=MARKET&price=0&product={position.product}&quantity={abs(quantity)}&trigger_price=0&validity=DAY&user_order_id={order_id}&client_id={broker.client_id}'
        headers = {
            'x-device-type': 'WEB',
            'client_id': broker.client_id,
            'Authorization': f'Bearer {broker.access_token}'
        }
        response = requests.request("POST", url, headers=headers, data={})
        response = response.json()
        print(':: TRADE ORDER SQURE OFF:: RESPONSE :: ', response, ' ::')

        if 'status' in response and response['status'] != 'error':    
            try:
                oms_order_id = response['data']['oms_order_id']
                position.oms_order_id = oms_order_id
                position.save()
                time.sleep(3)
                data = getPositions(broker.client_id, broker.access_token)
                dataList = data.get('data')
                order_resp = orderHistory(broker.client_id, broker.access_token , oms_order_id)
                ResponseLog.objects.create(response = f' ORDER HISTORY FUNCTION CALLED AFTER SQUARE OFF ORDER RESPONSE ========== {order_resp}')
                
                try:
                    if order_resp['data'][0]['status'] == "complete":
                        position_dict = [item for item in dataList if item.get('token') == int(position.token)]
                        Request = {"client_id":broker.client_id, "access_token": broker.access_token, "oms_order_id":response['data']['oms_order_id']}
                        ResponseLog.objects.create(response = f' SQUARE OFF ORDER FUNCTION CALLED RESPONSE ===Request body {Request}====response=== {order_resp} =========Position respons========={position_dict} ')
                        orderSide = order_resp['data'][0]['order_side']
                        
                        if position_dict:
                            # BUY / SELL CONDITION
                            if orderSide != position.order_side:
                                position.sellAvg = order_resp['data'][0]['avg_price']
                                position.buyQty = position_dict[0]['buy_quantity']
                                position.sellQty = position_dict[0]['sell_quantity']
                                position.qty = position_dict[0]['net_quantity']
                                position.remark = remark
                                position.save()

                                if position_dict[0]['net_quantity'] == 0:
                                    position.exitPrice = order_resp['data'][0]['avg_price']
                                    position.status = 'CLOSED'
                                    position.remark = remark
                                    position.is_exit = True
                                    position.save()

                                if position.currentQty and position.sellAvg and position.entryPrice :
                                    
                                    lot_size = int(position.currentQty)
                                    if position.order_side == 'BUY': pnl = round((position.sellAvg - position.entryPrice ) * lot_size,2)
                                    else: pnl = round((position.entryPrice - position.sellAvg) * lot_size, 2)

                                    if position.realizedPNL :
                                        position.realizedPNL = position.realizedPNL + pnl
                                        position.save()
                                    else:
                                        position.realizedPNL =  pnl 
                                        position.save()

                    elif order_resp['data'][0]['status'] == 'rejected':
                        position.fk_strategy.pos_status = 'REJECTED'
                        position.is_exit = True  
                        position.status = 'CLOSED'
                        position.fk_strategy.pos_remark = 'Order has been rejected'
                        position.remark = order_resp['data'][0]['reject_reason']
                        position.save()
                        position.fk_strategy.save()
                        
                        ResponseLog.objects.create(response = f' PLACE  ORDER REJECTEC RESPONSE ====response=== {order_resp}')
                        print(':: ORDER FAILED :: USER :: BROKER :: MASTERTRUST :: RESPONSE :: ', response)
                except:
                    ErrorLog.objects.create(error=traceback.format_exc())
                    traceback.print_exc()
            except:
                ErrorLog.objects.create(error=traceback.format_exc())
                traceback.print_exc()
            print(':: ORDER PLACED :: USER :: BROKER :: MASTERTRUST :: RESPONSE :: ', response)
        else:
            print(':: ORDER FAILED :: USER :: BROKER :: MASTERTRUST :: RESPONSE :: ', response)
            position.fk_strategy.pos_remark = response.get('message') if 'message' in response else 'Order Rejected'
            position.fk_strategy.pos_status = 'REJECTED'
            position.is_exit = True  
            position.fk_strategy.save()
    except:
            traceback.print_exc()
            return False


# SELL OR BUY ORDER EXECUTION

def sellBuyQuantity(position, quantity,order_side, broker, orderType):
    try:
        order_id = random.randrange(1, 10 ** 30)
        
        # order side : BUY / SELL
        # order Type : LIMIT / MARKET
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/orders?disclosed_quantity=0&exchange={position.exchange}&instrument_token={position.token}&market_protection_percentage=0&order_side={order_side}&order_type={orderType}&price=0&product={position.order_type}&quantity={abs(quantity)}&trigger_price=0&validity=DAY&user_order_id={order_id}&client_id={broker.client_id}'
    
        headers = {
            'x-device-type': 'WEB',
            'client_id': broker.client_id,
            'Authorization': f'Bearer {broker.access_token}'
        }
        response = requests.request("POST", url, headers=headers, data={})
        response = response.json()
        oms_order_id = response['data']['oms_order_id']
        orderHist = orderHistory(broker.client_id, broker.access_token , oms_order_id)
        try:
            order_status = orderHist['data'][0]['status'] 
        except:
            order_status = 'Success'
        if response.get('status') == 'success':
            return True
    except:
        traceback.print_exc()
        return False

############################################# get positions
def getPositions(client_id, access_token):
    url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/positions?type=historical&client_id={client_id}'

    headers = {
        'x-device-type': 'WEB',
        'client_id': client_id,
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers, data={})
    response = response.json()
    
    return response

############################################# get order book
def getOrderBook(broker):
    try:
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/orders?type=all&client_id={broker}'

        headers = {
            'x-device-type': 'WEB',
            'client_id': broker,
            'Authorization': f'Bearer {broker}'
        }

        response = requests.request("GET", url, headers=headers, data={})
        sorted_data = sorted(response.json()['data']['orders'], key=lambda item: int(item['order_entry_time']), reverse=True)
        
        return sorted_data
    except:
        traceback.print_exc()
    return []



############################################# get trade book
def getTradeBook(broker):
    try:
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v1/trades?client_id={broker.client_id}'

        headers = {
            'x-device-type': 'WEB',
            'client_id': broker.client_id,
            'Authorization': f'Bearer {broker.access_token}'
        }

        response = requests.request("GET", url, headers=headers, data={})
        # response = response.json()['data']['trades']

        response = requests.request("GET", url, headers=headers, data={})
        sorted_data = sorted(response.json()['data']['trades'], key=lambda item: int(item['order_entry_time']), reverse=True)
        
        return sorted_data
    except:
        traceback.print_exc()
    return []



################################################# modify open orders
def modifyOrder(data):
    try:
        url = f"https://masterswift-beta.mastertrust.co.in/api/v1/orders?client_id={data.get('client_id')}&oms_order_id={data.get('orderId')}&disclosed_quantity=0&exchange=NFO&instrument_token={data.get('token')}&order_type=LIMIT&price={data.get('modifyPrice')}&product={data.get('product')}&quantity={data.get('modifyQuantity')}&trigger_price=0&validity=DAY"

        headers = {
            'x-device-type': 'WEB',
            'client_id': data.get('client_id'),
            'Authorization': f'Bearer {data.get("access_token")}'
        }
        response = requests.request("PUT", url, headers=headers, data={})
        response = response.json()
        
        print(':: TRADE ORDER :: RESPONSE :: ', response, ' ::')
        
        if response.get('status') == 'success':
            return True
    except:
        traceback.print_exc()
    return False

################################################# Cancel open order
def cancelOrder(broker, data):
    try:
        url = f"https://masterswift-beta.mastertrust.co.in/api/v1/orders/{data.get('orderId')}?client_id={data.get('clientId')}"

        headers = {
            'x-device-type': 'WEB',
            'client_id': broker.Mtrust_client_id,
            'Authorization': f'Bearer {broker.Mtrust_access_token}'
        }
        response = requests.request("DELETE", url, headers=headers, data={})
        response = response.json()

        print(':: TURBO TRADE CANCEL ORDER :: RESPONSE :: ', response, ' ::')
        if response.get('status') == 'success':
            return True
    except:
        traceback.print_exc()
    return False


################################################# CANDLE DATA ###################################################
import traceback,time, requests
import pandas as pd

def get_candle_data(strategy, exch, token, start_time, end_time, duration, full_data=False):
    try:
        from .truedataAPI import trudata_api
        active_feed = MarketFeed.objects.last()
        url = ''
        response = None
        if active_feed and active_feed.market_data == 'MASTERTRUST':
            url = f'https://masterswift-beta.mastertrust.co.in/api/v1/charts/tdv?exchange={exch}&token={token}&candletype=1&starttime={start_time}&endtime={end_time}&data_duration={duration}'
            print("------url-------", url)
            response = requests.request("GET", url)
            data = response.json()
            if data :
                data = data['data']['candles']
            else:
                data = None
        else:
            update_start_time = dt.fromtimestamp(start_time)
            update_end_time = dt.fromtimestamp(end_time)
            from_tm = update_start_time.strftime('%y%m%dT%H:%M:%S')
            to_tm = update_end_time.strftime('%y%m%dT%H:%M:%S')
            symbol = trudata_api.gettoken(token)
            url = f'https://history.truedata.in/getbars?symbol={symbol}&from={from_tm}&to={to_tm}&response=json&interval={duration}min'
            headers = { 'Authorization': f'Bearer {trudata_api.truedata_obj.access_token}' }
            response = requests.request("GET", url , headers= headers )
            data = response.json()
            if 'Records' in data and data['Records'] != '':
                data = data['Records']
            else:
                data = None
        if data:
            df = None
            if active_feed and active_feed.market_data == 'MASTERTRUST':
                df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            else:
                df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'ExtraColumn'])
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values(by='Date', ascending=True, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.reset_index(drop=True)
        
        if full_data:
            return df if data else {}
        else:
            return {
                'p1cc': df.iloc[0].to_dict() if data else {},
            }
    except:
        traceback.print_exc()
        return {'p1cc': {}, 'p2cc' : {}}


mastertrust_data = DataManager()


def OrderChanges(change_type, *args, **kwargs):
    try:
        if change_type == 'square_off_order':
            order_obj = kwargs.get('order_obj')
            remark = kwargs.get('remark')
            broker = BrokerAccount.objects.filter(fk_user_id = order_obj.fk_strategy.fk_strategy.fk_user.id).last()
            square_off_qty = order_obj.qty
            if 'partial_qty' in kwargs:
                square_off_qty = kwargs['partial_qty']
                order_obj.currentQty = square_off_qty
                order_obj.save()
            else:
                order_obj.currentQty = square_off_qty
                order_obj.save()
            squareOffPosition(order_obj, square_off_qty, broker, remark)
            order_monitoring(broker, order_obj, remark)
    except: 
        ErrorLog.objects.create(error=traceback.format_exc())

