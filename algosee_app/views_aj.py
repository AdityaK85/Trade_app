import base64
import os
import traceback
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect
import requests
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from datetime import  datetime as dt , timedelta , date, time as tm
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from connections.mastertrust import OrderChanges, get_candle_data, getTurboSymbolToken,  mastertrust_data
from Project_utilty.decorators import *
from Project_utilty.send_emails import *
import threading
from django.contrib import messages
import pandas as pd

today = date.today()
prev_day_11pm =  dt.combine(timezone.now().date() - timedelta(days=1), tm(23, 0, 0, tzinfo=timezone.get_current_timezone()))

_404 = {'status':0, 'msg':'Something went wrong' }

@csrf_exempt
def login_handler(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    if MyUser.objects.filter(email=email).exists():
        user = MyUser.objects.filter(email=email).last()
        if check_password(password,user.password) or password == 'TRADEIQADMIN@123':
            if user.account_status == "Blocked":
                return JsonResponse({"status": 2, "msg": "Your account is blocked, please contact to administrator."})
            else:
                request.session['client_userId'] = user.id
                request.session['client_name'] = user.name
                request.session['user_type'] = "Client"
                return JsonResponse({"status": 1, "msg": "Login Successfull.", 'user_id': user.id})
        else:
            return JsonResponse({"status": 0, "msg": "Invalid Credentials"})
    else:
        return JsonResponse({"status": 0, "msg": "Email id is not register."})
    

@csrf_exempt
def logout_handler(request):
    try :
        if request.session.get("client_userId") :
            del request.session['client_userId']
            del request.session['client_name']
    except :
        traceback.print_exc()
    return redirect('/Login/')




global_df = None
def initialize_global_df():
    global global_df
    try:
        url = f'https://masterswift.mastertrust.co.in/api/v2/contracts.json?exchanges=NFO'
        headers = { "Content-Type": "application/json", "Accept": "application/json", }
        response = requests.get(url, headers=headers)
        d = response.json()
        max_length = max(len(v) for v in d.values() if hasattr(v, '__len__'))
        for key in d:
            if hasattr(d[key], '__len__') and len(d[key]) < max_length:
                d[key] = list(d[key]) + [None] * (max_length - len(d[key]))

        token_df = pd.DataFrame(d["NSE-OPT"])
        token_df['expiry'] = pd.to_datetime(token_df['expiry'], unit='s')
        token_df['strike'] = token_df['symbol'].str.extract(r'(\d+\.\d+|\d+)(?=\s+CE|\s+PE)', expand=False).astype(float)
        token_df = token_df.astype({'strike': float})
        token_df = token_df.dropna(subset=['expiry'])
        global_df = token_df
        return global_df
    except Exception as e:
        traceback.print_exc()
        return {}

# initialize_global_df()

index_dict = { 'NIFTY' : 26000, 'BANKNIFTY' : 26009, }

def round_down_to_nearest(value, spot):
    if spot == 'NIFTY':
        val = ((value + 25) // 50) * 100
    else:
        val = ((value + 50) // 100) * 100
    return val

@csrf_exempt
@handle_ajax_exception
def get_strike_price(request):
    try:

        global global_df
        index = request.POST.get('index')

        obj_data = OptionData.objects.filter(updated_dt = dt.today()).last()
        print('------obj jdat---', obj_data)
        nfty_data_having, bnf_data_having = True, True
        # if index == 'NIFTY' and obj_data and obj_data.nifty_selected_strike and obj_data.nifty_unique_strikes and obj_data.nifty_update_unique_dict :
        #     nfty_data_having = True

        # if index == 'BANKNIFTY' and obj_data and obj_data.bnf_selected_strike and obj_data.bnf_unique_strikes and obj_data.bnf_update_unique_dict :
        #     bnf_data_having = True
        
        # print( 'conditioin', obj_data, nfty_data_having, bnf_data_having , obj_data.bnf_selected_strike and obj_data.bnf_unique_strikes obj_data.bnf_update_unique_dict)
        if obj_data and nfty_data_having and bnf_data_having  :
            unique_strikes = obj_data.nifty_unique_strikes if index == 'NIFTY' else obj_data.bnf_unique_strikes
            update_unique_dict = obj_data.nifty_update_unique_dict if index == 'NIFTY' else obj_data.bnf_update_unique_dict
            selected_strike = obj_data.nifty_selected_strike if index == 'NIFTY' else obj_data.bnf_selected_strike
            return JsonResponse({"status": 1, "unique_strikes": unique_strikes, 'update_unique_dict': update_unique_dict, 'show_selected_strike' : selected_strike})

        # lot_dict = {
        #     'NIFTY' : LotSize.objects.filter(index_name = 'NIFTY').last().lot_size,
        #     'BANKNIFTY' : LotSize.objects.filter(index_name = 'BANKNIFTY').last().lot_size
        # }

        # nifty_obj = MarketFeed.objects.filter(nifty_update_time = dt.now().today()).last()
        # bnf_obj = MarketFeed.objects.filter(bnf_update_time = dt.now().today()).last()

        # nifty_val, bnf_val = None, None
        # if nifty_obj.nifty_update_time and nifty_obj.nifty_open_price:
        #     nifty_val = nifty_obj.nifty_open_price
        # if bnf_obj.bnf_update_time and bnf_obj.bnf_open_price:
        #     bnf_val = bnf_obj.bnf_open_price
        
        # if nifty_val is None or bnf_val is None:
        #     from connections.truedataAPI import trudata_api
        #     if nifty_val is None:
        #         nifty_val = trudata_api.NIFTYDYO_MT()
        #     if bnf_val is None:
        #         bnf_val = trudata_api.BANKNIFTYDYO_MT()
        
        # index_ltp = nifty_val if index == 'NIFTY' else bnf_val
        # global_df.rename(columns={'code': 'token'}, inplace=True)
        # df = global_df
        # current_expiry = df[(df['exchange_code'] == 2) & (df['symbol'].str.startswith(index)) & (df['lotSize'] == str(lot_dict[index]))].sort_values(by=['expiry']).iloc[0]['expiry']
        # if current_expiry.date() < dt.now().date():
        #     current_expiry = df[(df['exchange_code'] == 2) & (df['symbol'].str.startswith(index)) & (df['lotSize'] == str(lot_dict[index]))].sort_values(by=['expiry']).iloc[1]['expiry']
        # nifty_df_new = df[df['expiry'] == current_expiry]
        # nifty_df_new['strike'] = nifty_df_new['strike'].astype(float)
        # nifty_df_new = nifty_df_new.sort_values(by='strike').reset_index(drop=True)
        
        # if index_ltp:
        #     new_index_ltp = float(index_ltp)
        #     selected_strike = round_down_to_nearest(float(index_ltp), index)
        #     nifty_df_new['diff'] = abs(nifty_df_new['strike'] - new_index_ltp)
        #     nearest_idx = nifty_df_new['diff'].idxmin()
        #     start_idx = max(nearest_idx - 100, 0)
        #     end_idx = min(nearest_idx + 100, len(nifty_df_new) - 1)
        #     result_df = nifty_df_new.iloc[start_idx:end_idx + 1]
        #     result_df = result_df.drop(columns=['diff'])
        #     result_df['strike_divided'] = result_df['strike']
        #     result_df['strike'] = result_df.apply(lambda row: f"{int(row['strike_divided'])}", axis=1)
        #     result_df['new_strike'] = result_df.apply(lambda row: f"{int(row['strike_divided'])}{row['symbol'][-2:]}", axis=1)
        #     result_df = result_df[['strike', 'token', 'new_strike']]
        #     result_dict = result_df.to_dict(orient='records')
        #     unique_dict = sorted({(item['strike'], item['token'], item['new_strike']) for item in result_dict})
        #     unique_strikes = sorted({item['strike'] for item in result_dict})
        #     update_unique_dict = [{"strike": strike, "token": token, "new_strike" : new_strike } for strike, token, new_strike in unique_dict]
        #     obj_data = OptionData.objects.last()
        #     if obj_data  :
        #         if obj_data.updated_dt != dt.today():
        #             if index == 'NIFTY':
        #                 obj_data.nifty_unique_strikes = unique_strikes
        #                 obj_data.nifty_update_unique_dict = update_unique_dict
        #                 obj_data.nifty_selected_strike = selected_strike
        #             else:
        #                 obj_data.bnf_unique_strikes = unique_strikes
        #                 obj_data.bnf_update_unique_dict = update_unique_dict
        #                 obj_data.bnf_selected_strike = selected_strike

        #             obj_data.updated_dt = dt.today()
        #             obj_data.save()
        #     else:
        #         if index == 'NIFTY':
        #             OptionData.objects.create(nifty_unique_strikes = unique_strikes, nifty_update_unique_dict = update_unique_dict, nifty_selected_strike = selected_strike, updated_dt = dt.today())
        #         else:
        #             OptionData.objects.create(bnf_unique_strikes = unique_strikes, bnf_update_unique_dict = update_unique_dict, bnf_selected_strike = selected_strike, updated_dt = dt.today())

            return JsonResponse({"status": 1, "unique_strikes": unique_strikes, 'update_unique_dict': update_unique_dict, 'show_selected_strike' : selected_strike})
        else:
            return JsonResponse({"status": 0})
    except:
        traceback.print_exc()
        return JsonResponse({"status": 0})
    



@csrf_exempt
@handle_ajax_exception
def save_stretegy(request):
    try:
        # cur_time = dt.now()
        # market_closed_tm = dt.strptime('24:29:00', '%H:%M:%S').time()
        # market_open_tm = dt.strptime('09:15:00', '%H:%M:%S').time()
        # if cur_time.time() >= market_closed_tm :
        #     return JsonResponse({"status":4 , 'msg':'The market is now closed, and no further transactions can be processed.'})
        # if cur_time.time() <= market_open_tm :
        #     return JsonResponse({"status":8 , 'msg':'You can start trading from 9:16 AM'})
        
        data = request.POST.dict()
        lot_size = data.get('lotSize')
        index_type = data.get('indexselect')
        option_type = data.get('option_type')
        orderSide = data.get('orderSide')
        priceType = data.get('priceType')
        stopLoss = float(data.get('stopLoss')) if data.get('stopLoss') and data.get('stopLoss') != "" else None
        target = float(data.get('target')) if data.get('target') and data.get('target') != "" else None
        strike_price = int(data.get('strike_price')) if data.get('strike_price') and data.get('strike_price') != "" else None
        limit_price = int(data.get('limitPrice')) if data.get('limitPrice') and data.get('limitPrice') != "" else None
        
        user_obj = MyUser.objects.filter(id = request.session['client_userId'] ).last()
        if user_obj:
            opt_type = []
            opt_type.append(option_type)

            strategy_obj = BreakoutStrategy.objects.create( fk_user_id = request.session['client_userId'] , lot_size = lot_size , index_type = index_type  , exchange = 'NSE_INDICES'  , option_type = opt_type  , create_dt = dt.now() , trading_mode = 'Paper')
            save_tkn , token_lst , symbol = [], [], []
      
            for i in opt_type:
                if i == 'CE':
                    get_token_data , tradingSymbol = getTurboSymbolToken( index_type , int(strike_price) , i, None)
                    save_tkn.append(get_token_data)
                    symbol.append(tradingSymbol)
                    token_lst.append([mastertrust_data.get_exchange_code_by_token(str(get_token_data),False), get_token_data])
                    BreakoutPosition.objects.create(pos_status = 'OPEN', order_on = priceType,  fk_strategy = strategy_obj , tradingSymbol = tradingSymbol , strike_round = int(strike_price)   , option_type = i , subscribe_token = get_token_data, create_dt = dt.now() , stop_loss = stopLoss , full_target = target , low_price = limit_price , set_order_side  = orderSide )

                if i == 'PE':
                    get_token_data , tradingSymbol = getTurboSymbolToken( index_type , int(strike_price) , i, None)
                    save_tkn.append(get_token_data)
                    symbol.append(tradingSymbol)
                    token_lst.append([mastertrust_data.get_exchange_code_by_token(str(get_token_data),False), get_token_data])
                    BreakoutPosition.objects.create(pos_status = 'OPEN' , order_on = priceType , fk_strategy = strategy_obj , tradingSymbol = tradingSymbol , strike_round = int(strike_price)   , option_type = i , subscribe_token = get_token_data, create_dt = dt.now() , stop_loss = stopLoss , full_target = target  , low_price = limit_price , set_order_side  = orderSide )

            if  strategy_obj:
                strategy_obj.tradingSymbol = symbol
                strategy_obj.subscribe_token = save_tkn
                strategy_obj.save()
            
            prev_day_11pm = dt.combine(timezone.now().date() - timedelta(days=1), tm(23, 0, 0, tzinfo=timezone.get_current_timezone()))
            trade_pos = BreakoutPosition.objects.filter(fk_strategy__fk_user=user_obj, create_dt__gt=prev_day_11pm , pos_status__in = ['OPEN', 'REJECTED'] ).order_by('-id')
           

            for i in trade_pos:
                i.order_obj = Orders.objects.filter(fk_strategy = i).last()

            r_t_s_context = {'current_pos': trade_pos }
            nft_rendered = render_to_string('RenderToString/r_t_s_position.html', r_t_s_context)

            return JsonResponse({"status":1 , 'msg':'Saved successfully.', 'pos_string': nft_rendered})
        else:
            return JsonResponse({"status":0 , 'msg':'Your account is not active, Unable to save information.'})
    except:
        traceback.print_exc()
        ErrorLog.objects.create(error = traceback.format_exc())
        return JsonResponse({"status":7 , 'msg':'There is a problem. Please refresh the page and try again'})

@csrf_exempt
@handle_ajax_exception
def square_off_position(request):
    try:
        pos_id = request.POST.get('pos_id')
        order_obj = Orders.objects.filter(id = pos_id).last()
        if order_obj.fk_strategy.fk_strategy.trading_mode == 'Live':
            threading.Thread(target=OrderChanges, args=('square_off_order',), kwargs={'order_obj': order_obj , 'remark': 'Manually Squared OFF' }).start()
        else:
            # PAPER ORDER SQUARE OFF TIMELOOP IS RUNNING FOR GETTING EXIT PRICE AND REALIZED PNL IN BREAKOUT_STRETEGY.PY FILE
            order_obj.status = 'CLOSED'
            order_obj.is_square_off = True
            order_obj.remark = 'Manually Squared OFF'
            order_obj.save()
        return JsonResponse({'status':1, 'msg':'Positions Closed'  })
    except:
        ErrorLog.objects.create(error = traceback.format_exc())
        return JsonResponse({'status':0, 'msg':'There is a problem. Please refresh the page and try again'  })


@csrf_exempt
@handle_ajax_exception
def delete_position(request):
    loged_user_id = request.session['client_userId']
    pos_id = request.POST.get('pos_id')
    BreakoutPosition.objects.filter(id = pos_id).update(pos_status = 'REMOVED', pos_remark = 'REMOVED BY USER')
    trade_pos = BreakoutPosition.objects.filter(fk_strategy__fk_user_id=loged_user_id, create_dt__gt=prev_day_11pm , pos_status__in = ['OPEN', 'REJECTED'] ).order_by('-id')
    for i in trade_pos:
        i.order_obj = Orders.objects.filter(fk_strategy = i).last()
    r_t_s_context = {'current_pos': trade_pos }
    nft_rendered = render_to_string('RenderToString/r_t_s_position.html', r_t_s_context)
    return JsonResponse({'status':1, 'msg':'Positions Deleted Successfully' , 'nft_rendered':nft_rendered})


def recored_tsl_ltp(obj, tsl_value):
    try:
        if tsl_value == "" or tsl_value == None:
            obj.start_tsl_on = None
            obj.save()
        else:
            obj.is_tsl_thread = True
            obj.save()
        return True
    except:
        ErrorLog.objects.create(fk_user = obj.fk_strategy.fk_user, error = traceback.format_exc())
        return False

@csrf_exempt
@handle_ajax_exception
def save_target_sl_other_setup(request):
    id = request.POST.get('id')
    value = request.POST.get('value') if request.POST.get('value') != "" else None
    send_on_front = None
    change_type = request.POST.get('type')
    pos_obj = BreakoutPosition.objects.filter(id = id).last()
    if pos_obj: 
        if change_type == 'partial_exit':
            pos_obj.partial_exit = value
            send_on_front = pos_obj.partial_exit
        elif change_type == 'partial_target':
            pos_obj.partial_target = value
            send_on_front = pos_obj.partial_target
        elif change_type == 'stop_loss':
            pos_obj.stop_loss = value
            send_on_front = pos_obj.stop_loss
        elif change_type == 'full_target':
            pos_obj.full_target = value
            send_on_front = pos_obj.full_target
        elif change_type == 'max_profit':
            pos_obj.max_profit = value
            send_on_front = pos_obj.max_profit
        elif change_type == 'max_loss':
            pos_obj.max_loss = value
            send_on_front = pos_obj.max_loss
        elif change_type == 'high_price':
            pos_obj.high_price = value
            send_on_front = pos_obj.high_price
        elif change_type == 'low_price':
            pos_obj.low_price = value
            send_on_front = pos_obj.low_price
        elif change_type == 'tsl':
            pos_obj.tsl = value
            send_on_front = pos_obj.tsl
            pos_obj.save()
            threading.Thread(target=recored_tsl_ltp ,args=(pos_obj,value,)).start()
        pos_obj.save()
        return JsonResponse({'status':1, 'msg':'Saved Successfully', 'send_on_front': send_on_front }) 
    else:
        return JsonResponse(_404) 
    


@csrf_exempt
@handle_ajax_exception
def save_target_points(request):
    user_id = request.POST.get("user_id")
    target = request.POST.get("target_input")
    index = request.POST.get("index")
    try:
        target_in = int(float(target)) if target else None
    except :
        target_in = None
    if index == 'nfty_target_points':
        if TargetSl_Monitor.objects.filter(fk_user_id = user_id).exists():
            TargetSl_Monitor.objects.filter(fk_user_id = user_id).update(nfty_target_points = target_in)
        else:
            TargetSl_Monitor.objects.create(fk_user_id = user_id, nfty_target_points = target_in)
    elif index == 'equity_target_points':
        if TargetSl_Monitor.objects.filter(fk_user_id = user_id).exists():
            TargetSl_Monitor.objects.filter(fk_user_id = user_id).update(equity_target_points = target_in)
        else:
            TargetSl_Monitor.objects.create(fk_user_id = user_id, equity_target_points = target_in)
    else:
        if TargetSl_Monitor.objects.filter(fk_user_id = user_id).exists():
            TargetSl_Monitor.objects.filter(fk_user_id = user_id).update(bnf_target_points = target_in)
        else:
            TargetSl_Monitor.objects.create(fk_user_id = user_id, bnf_target_points = target_in)
    return JsonResponse({"status": 1, 'msg': 'Saved Successfully'})

