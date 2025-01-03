import json
import threading
import traceback
from connections.live_data import data_dict
from timeloop import Timeloop
from datetime import datetime as dt, timedelta, time, date
from django.utils import timezone
from time  import sleep
from algosee_app.models import *
from connections.mastertrust import  OrderChanges, PlacePaperOrder, get_candle_data, placeOrder
from asgiref.sync import async_to_sync
from collections import defaultdict
from channels.layers import get_channel_layer
from connections.order_utility import order_monitoring
from django.db.models import Q
import pandas as pd
import time as tm

lot_dict = {
    'NIFTY' : LotSize.objects.filter(index_name = 'NIFTY').last().lot_size,
    'BANKNIFTY' : LotSize.objects.filter(index_name = 'BANKNIFTY').last().lot_size
}

prev_day_11pm = dt.combine(timezone.now().date() - timedelta(days=1), time(23, 0, 0, tzinfo=timezone.get_current_timezone()))
# MARKET AVAIBILITY
check_day = date.today().weekday()
def check_market_avaibility():
	global check_day
	# if check_day >= 0 and check_day <= 4:
	# 	check_time = dt.now().time()	
	# 	if (check_time >= time(9,16) and check_time <= time(15,30)):
	# 		return True
	# return False
	return True

monitor_spot = Timeloop()
@monitor_spot.job(interval=timedelta(seconds=1))
def high_low_monitor():
	# GET HIGH AND LOW LTP
	try:
		marketTm = check_market_avaibility()
		if marketTm:
			global prev_day_11pm
			
			place_order_obj = BreakoutPosition.objects.filter(Q(pos_status = 'OPEN') &  Q(order_on__in = ['Market','Limit']) & Q(create_dt__gt=prev_day_11pm))

			for order_obj in place_order_obj:
				
				ltp_dict  = data_dict.get(str(order_obj.subscribe_token))
				try:
					if ltp_dict is not None and ltp_dict.get('ltp', 0) is not None :
						compare_low_price = order_obj.low_price if order_obj and order_obj.low_price else 0
						execute_order = False
						order_side = order_obj.set_order_side

						if order_obj.order_on == 'Market' :   # Market Order Placed
							execute_order = True

						elif (float(ltp_dict.get('ltp', 0)) <= float(compare_low_price) ) and (order_obj and order_obj.low_price and order_obj.order_on == 'Limit'):  # Limit Orders Placed
							execute_order = True
						
						if execute_order:
							qty = int(order_obj.fk_strategy.lot_size) * lot_dict[order_obj.fk_strategy.index_type] 
							 
							data = {
									'strategy': order_obj.id,
									'exchange' : 'NFO',
									'token': order_obj.subscribe_token,
									'orderSide': order_side,
									'orderType': order_obj.option_type,
									'product':'MIS',
									'ltp': ltp_dict.get('ltp', 0) ,
									'quantity': qty,
									'symbol' : order_obj.tradingSymbol,
									'order_mode':'Paper',
							}
							if order_obj.monitoring_flag:
								PlacePaperOrder(data)
								order_obj.monitoring_flag = False
								order_obj.save()
								update_td = {
									'tr_id': order_obj.id,
									'full_target': order_obj.full_target,
									'stop_loss': round(order_obj.stop_loss, 2) if order_obj.stop_loss else None ,
									'order_side' : order_side
								}
								async_to_sync(channel_layer.group_send)(
									"Test_Consumer",
									{
										"type": "send_live_data",
										"value": {'target_update': update_td  }
									}
								) 
					# try:
					# 	if ltp_dict and 'ltp' in ltp_dict and ltp_dict['ltp'] is not None:  monitor_tsl_price(order_obj, ltp_dict.get('ltp',0))
					# except:traceback.print_exc()
				except: 
					traceback.print_exc()
					ErrorLog.objects.create(error=traceback.format_exc())
	except:
		traceback.print_exc()
		ErrorLog.objects.create(error=traceback.format_exc())

channel_layer = get_channel_layer()

def realized_pnl(ltp, entry_price, lot_size, order_side):
	try:
		if order_side == 'BUY': pnl = round((ltp - entry_price )* lot_size,2)
		else: pnl = round((entry_price - ltp) * lot_size, 2)
	except:pnl = 0
	return pnl

def exit_all_orders(order_obj, remark, pnl):
	try:
		global prev_day_11pm
		orders = Orders.objects.filter(fk_strategy__fk_strategy__fk_user__id = order_obj , status= 'OPEN' , is_exit = False,  created_at__gt=prev_day_11pm)
		for i in orders:
			# if i.fk_strategy.fk_strategy.trading_mode == 'Live':
			# 	threading.Thread(target=OrderChanges, args=('square_off_order',), kwargs={'order_obj': i , 'remark': remark }).start()
			# 	i.is_exit = True
			# 	i.save()
			# else:
				order_ltp = float(data_dict.get(str(i.token)).get('ltp'))
				pnl_key = f'pnl_{i.fk_strategy.id}'
				ordre_pnl =  pnl.get(pnl_key)
				i.status = 'CLOSED'
				i.exitPrice = order_ltp
				i.realizedPNL = float(ordre_pnl) + float(i.realizedPNL) if i.realizedPNL else ordre_pnl
				i.remark = remark if not i.remark else remark
				i.is_exit = True
				i.save()
	except: ErrorLog.objects.create(error=traceback.format_exc())	

def exit_order(order_obj, ltp, pnl, remark, partial_qty = None , confirm = None , not_closed_all = False):
	import time
	global prev_day_11pm
	if not_closed_all:
		if confirm == 'partial_exit':
			# if order_obj.fk_strategy.fk_strategy.fk_user.trading_mode == 'Live':
			# 	threading.Thread(target=OrderChanges, args=('square_off_order',), kwargs={'order_obj': order_obj , 'remark': remark ,'partial_qty': partial_qty }).start()
			# else:
			order_obj.buyQty = int(order_obj.buyQty) -  partial_qty
			order_obj.sellQty = partial_qty
			order_obj.sellAvg = ltp
		else:
			# if order_obj.fk_strategy.fk_strategy.fk_user.trading_mode == 'Live':
			# 	if order_obj.status == 'OPEN':
			# 		threading.Thread(target=OrderChanges, args=('square_off_order',), kwargs={'order_obj': order_obj , 'remark': remark }).start()
			# else:
			order_obj.sellQty = int(order_obj.buyQty) if order_obj.buyQty else 0
			order_obj.sellAvg = ltp
			order_obj.status = 'CLOSED'
			order_obj.exitPrice = ltp
		# if order_obj.fk_strategy.fk_strategy.fk_user.trading_mode == 'Paper':
		order_obj.realizedPNL = float(pnl) + float(order_obj.realizedPNL) if order_obj.realizedPNL else pnl
		order_obj.remark = remark
		order_obj.save()
	else:
		try: exit_all_orders(order_obj, remark, pnl)
		except: ErrorLog.objects.create(error=traceback.format_exc())	
# ######################### MAIN FUNCTINOS ####################
monitor_mtm_pnl = Timeloop()
@monitor_mtm_pnl.job(interval=timedelta(seconds=1))
def monitor_mtm_pnl_order():
	try:
		global prev_day_11pm
		order_obj = Orders.objects.filter(status='OPEN', fk_strategy__pos_status = 'OPEN',  created_at__gt=prev_day_11pm,is_exit = False).select_related( 'fk_strategy__fk_strategy__fk_user').only( 'entryPrice', 'exitPrice', 'buyQty', 'order_side', 'remark', 'fk_strategy__partial_exit', 'fk_strategy__partial_target', 'fk_strategy__full_target', 'fk_strategy__max_profit', 'fk_strategy__max_loss', 'fk_strategy__fk_strategy__fk_user__id', 'token', 'remark','is_exit')
		user_mtm = defaultdict(float)
		pnl_dict = {}
		for i in order_obj:
			pnl = calculate_pnl(i)
			mtm_key = f'user_{i.fk_strategy.fk_strategy.fk_user.id}'
			user_mtm[mtm_key] += pnl
			try: monitor_pnl(i, pnl, mtm_key)
			except: ErrorLog.objects.create(error=traceback.format_exc())
			pnl_key = f'pnl_{i.fk_strategy.id}'
			pnl_dict[pnl_key] = pnl
			if i.fk_strategy.fk_strategy.trading_mode == 'Live':
				broker =  BrokerAccount.objects.filter(fk_user_id = i.fk_strategy.fk_strategy.fk_user.id ).last()
				try:threading.Thread(target=order_monitoring, args=(broker, i , )).start()
				except: ErrorLog.objects.create(error=traceback.format_exc())
		# ADDED CLOSED ORDERS MTM 
		closed_orders = Orders.objects.filter(status='CLOSED', fk_strategy__pos_status = 'OPEN', created_at__gt=prev_day_11pm).select_related('fk_strategy__fk_strategy__fk_user').only('realizedPNL', 'fk_strategy__fk_strategy__fk_user__id')
		for i in closed_orders:
			if i.fk_strategy.fk_strategy.fk_user.trading_mode == i.fk_strategy.fk_strategy.trading_mode:
				mtm_key = f'user_{i.fk_strategy.fk_strategy.fk_user.id}'
				user_mtm[mtm_key] += float(i.realizedPNL) if i.realizedPNL else 0
		try: send_live_data(pnl_dict, user_mtm)
		except: ErrorLog.objects.create(error=traceback.format_exc())
		try:monitor_overall_pnl(user_mtm, pnl_dict)
		except: ErrorLog.objects.create(error=traceback.format_exc())
	except: ErrorLog.objects.create(error=traceback.format_exc())
# ################################ HELPER FUNCTIONS ##############################
def monitor_tsl_price(order_obj, ltp): # MONITOR TSL INCREASE TSL BY ENTERED POINTS
	if order_obj and order_obj.fk_strategy and order_obj.start_tsl_on and order_obj.tsl:
		tsl = float(order_obj.start_tsl_on )
		sl = float(order_obj.stop_loss) if order_obj.stop_loss else 0
		tsl_point = int(order_obj.tsl)
		open_order_obj = Orders.objects.filter(fk_strategy = order_obj, status='OPEN', fk_strategy__pos_status = 'OPEN',  created_at__gt=prev_day_11pm,is_exit = False).last()
		if ltp >= tsl and open_order_obj:
			try:
				order_obj.start_tsl_on = tsl + tsl_point
				if open_order_obj.order_side == 'BUY': order_obj.stop_loss = sl + tsl_point
				else: order_obj.stop_loss = sl - tsl_point
				order_obj.save()
				update_td = {
					'tr_id': order_obj.id,
					'stop_loss': order_obj.stop_loss,
				}
				async_to_sync(channel_layer.group_send)(
					"Test_Consumer",
					{
						"type": "send_live_data",
						"value": {'tsl_sl_update': update_td  }
					}
				) 
			except: traceback.print_exc()

def calculate_pnl(order):   # CALCULATE PNL OF EACH SEPRATE POSITION
	try:
		ltp = float(data_dict.get(str(order.token)).get('ltp'))
		entry_price = float(order.entryPrice) 
		exit_price = None
		lot_size = 0
		if order.fk_strategy.fk_strategy.index_type == 'EQUITY': lot_size = int(order.fk_strategy.fk_strategy.lot_size)
		else:lot_size = int(order.fk_strategy.fk_strategy.lot_size)  * lot_dict.get(order.fk_strategy.fk_strategy.index_type)
		if order.order_side == 'BUY':
			pnl = round((ltp - entry_price) * lot_size, 2)
			if order.exitPrice:
				exit_price = float(order.exitPrice) 
				pnl = round((exit_price - entry_price) * lot_size, 2)
		else:
			pnl = round((entry_price - ltp) * lot_size, 2)
			if order.exitPrice:
				exit_price = float(order.exitPrice) 
				pnl = round((entry_price - exit_price) * lot_size, 2)
		if order.status == 'OPEN' and order.realizedPNL:
			pnl += float(order.realizedPNL) if order.realizedPNL else 0
		return pnl
	except: ErrorLog.objects.create(error=traceback.format_exc())

def monitor_pnl(order, pnl, mtm_key):  # MONITOR PNL OF SEPERATE EACH POSITION
	t_sl = order.fk_strategy
	ltp = float(data_dict.get(str(order.token)).get('ltp'))
	try: partial_exit = abs(int(t_sl.partial_exit)) if t_sl and t_sl.partial_exit else None
	except: partial_exit = None
	entry_price = float(order.entryPrice) if order and order.entryPrice else 0
	partial_target = abs(float(t_sl.partial_target) + entry_price ) if t_sl and t_sl.partial_target else None
	full_target = abs(float(t_sl.full_target)) if t_sl.full_target else None
	stop_loss = abs(float(t_sl.stop_loss)) if t_sl.stop_loss else None
	max_profit = abs(float(t_sl.max_profit)) if t_sl.max_profit else None
	max_loss = -abs(float(t_sl.max_loss)) if t_sl.max_loss else None
	if partial_exit and partial_target and ltp >= partial_target:
		if order.fk_strategy.fk_strategy.index_type == 'EQUITY' : partial_exit = int(partial_exit)
		else: partial_qty = partial_exit * lot_dict.get(order.fk_strategy.fk_strategy.index_type)
		realized_val = realized_pnl(ltp, order.entryPrice, partial_qty , order.order_side)
		remark = f'Partial Target Hit | Lot size : {partial_exit} | Target : {partial_target} '
		Available_lotSize = int(order.fk_strategy.fk_strategy.lot_size) - int(partial_exit)
		order.fk_strategy.fk_strategy.lot_size = Available_lotSize
		order.fk_strategy.fk_strategy.save()
		t_sl.partial_exit = None
		t_sl.partial_target = None
		t_sl.save()
		try: exit_order(order, ltp, realized_val, remark, partial_qty, 'partial_exit', True)
		except: ErrorLog.objects.create(error=traceback.format_exc())

	if order.order_side == 'BUY':
		exit_reason = None
		if max_loss and max_loss >= pnl  :		    ##### MONITOR ON MTM #####
			exit_reason = 'Max Loss Hit'					 		
		elif max_profit and pnl >= max_profit   :   ##### MONITOR ON MTM #####
			exit_reason = 'Max Profit Hit'						 
		elif stop_loss and abs(stop_loss) >= ltp  : ##### MONITOR ON LTP #####
			exit_reason = 'Stop Loss Hit'              
		elif full_target and ltp >= full_target  :  ##### MONITOR ON LTP #####
			exit_reason = 'Full Target Hit'
		if exit_reason : 
			order.is_exit = True                   
			order.save()
			try:exit_order(order, ltp, pnl, exit_reason ,None,None, True)
			except: ErrorLog.objects.create(error=traceback.format_exc())
			
	if order.order_side == 'SELL':	
		exit_reason = None
		if max_loss and max_loss >= pnl  :		    ##### MONITOR ON MTM #####
			exit_reason = 'Max Loss Hit'					 		
		elif max_profit and pnl >= max_profit   :   ##### MONITOR ON MTM #####
			exit_reason = 'Max Profit Hit'						 
		elif stop_loss and abs(stop_loss) <= ltp  : ##### MONITOR ON LTP #####
			exit_reason = 'Stop Loss Hit'              
		elif full_target and ltp <= full_target  :  ##### MONITOR ON LTP #####
			exit_reason = 'Full Target Hit'
		if exit_reason : 
			order.is_exit = True                   
			order.save()
			try:exit_order(order, ltp, pnl, exit_reason ,None,None, True)
			except: ErrorLog.objects.create(error=traceback.format_exc())

def send_live_data(pnl_dict=None, user_mtm=None, logged_user=None):  # SEND LIVE UPDATED ON FRONTED 
	try:
		data = {}
		if pnl_dict: data['monitor_pnl'] = json.dumps(pnl_dict)
		if user_mtm: data['monitor_mtm'] = json.dumps(user_mtm)
		if logged_user: data['logged_user'] = logged_user
		try:
			if channel_layer:
				async_to_sync(channel_layer.group_send)("Test_Consumer", {"type": "send_live_data", "value": data})
		except RuntimeError as e:
			error_text = f'Error while sending data: {str(e)}\n{traceback.format_exc()}'
			ErrorLog.objects.create(error=error_text)
	except:
		error_text = f'==================ERROR WHILE SENDING DATA TO FRONTEND==============={traceback.format_exc()}'
		ErrorLog.objects.create(error=error_text)

def remove_pending_position(fk_user_id, remove_when):    # REMOVE PENDING POSITION IF MARKET CLOSED AND RESET ALL TRADES
	global prev_day_11pm
	pos_obj = BreakoutPosition.objects.filter( pos_status = 'OPEN', fk_strategy__fk_user_id = fk_user_id,  create_dt__gt=prev_day_11pm )
	for i in pos_obj:
		if not Orders.objects.filter(fk_strategy_id = i.id).exists():
			if remove_when == 'Target': remark = 'OVER ALL PROFIT HITS'
			elif remove_when == 'SL': remark = 'OVER ALL LOSS HITS'
			else: remark = 'AUTO SQUARE OFF'
			i.pos_status = 'REMOVED'
			i.pos_remark = f'AUTO REMOVED BY SYSTEM ({remark})'
			i.save()
			async_to_sync(channel_layer.group_send)("Test_Consumer", {"type": "send_live_data", "value": {'delete_row_id': i.id} })

def monitor_overall_pnl(user_mtm, pnl_dict):  # MONITOR OVERALL MTM
	global prev_day_11pm
	try:
		for mtm_key in user_mtm.keys():
			user_id = int(mtm_key.split('_')[1])
			mtm_key = f'user_{user_id}'
			_mtm = user_mtm.get(mtm_key)
			tsm_obj = TargetSl_Monitor.objects.filter(fk_user_id=user_id).last()
			try:
				_target = None
				_sl = None
				user_obj = MyUser.objects.filter(id = user_id).last()
				cur_time = dt.now()
				square_off_time = dt.strptime('15:29:00', '%H:%M:%S').time()
				market_closed_tm = dt.strptime('15:30:00', '%H:%M:%S').time()
				open_order = Orders.objects.filter( fk_strategy__fk_strategy__fk_user_id = user_obj.id, status='OPEN', fk_strategy__pos_status = 'OPEN',  created_at__gt=prev_day_11pm, is_exit = False).exists()
				if cur_time.time() >= square_off_time and open_order :
					pass
					# try: exit_order(user_obj.id, None, pnl_dict, 'AUTO SQUARE-OFF MARKET TIME IS UP', None, None, False)
					# except: ErrorLog.objects.create(error=traceback.format_exc())
					# threading.Thread(target=remove_pending_position, args=(user_obj.id, 'SQUARE OFF',)).start()
				else:
					if user_obj.trading_mode == 'Live':
						_target = float(tsm_obj.live_target) if tsm_obj and tsm_obj.live_target else None
						_sl = float(tsm_obj.live_sl) if tsm_obj and tsm_obj.live_sl else None
					else:
						_target = float(tsm_obj.target) if tsm_obj and tsm_obj.target else None
						_sl = float(tsm_obj.sl) if tsm_obj and tsm_obj.sl else None
					if tsm_obj :
						if _target and _mtm >= _target:
							try: exit_order(user_obj.id, None , pnl_dict, 'Overall Profit Hit', None, None, False)
							except: ErrorLog.objects.create(error=traceback.format_exc())
							threading.Thread(target=remove_pending_position, args=(user_obj.id, 'Target',)).start()
							pass
							if user_obj.trading_mode == 'Live':
								tsm_obj.live_target = None
							else:
								tsm_obj.target = None
							tsm_obj.save()
							break
						elif _sl and _mtm <= -_sl:
							try:
								try:exit_order(user_obj.id, None, pnl_dict, 'Overall Loss Hit', None, None, False)
								except: ErrorLog.objects.create(error=traceback.format_exc())
								threading.Thread(target=remove_pending_position, args=(user_obj.id, 'SL',)).start()
								if user_obj.trading_mode == 'Live':
									tsm_obj.live_sl = None
								else:
									tsm_obj.sl = None
								tsm_obj.save()
								break
							except: traceback.print_exc()
			except: ErrorLog.objects.create(error=traceback.format_exc())
	except Exception as e:
		traceback.print_exc()
		ErrorLog.objects.create(error=traceback.format_exc())

def square_off_procession(order_obj):
	try:
		import time
		ltp_dict  = data_dict.get(str(order_obj.token))
		while ltp_dict is not None and order_obj.is_square_off :
			time.sleep(0.3)
			if ltp_dict is not None and ltp_dict.get('ltp') is not None:
				ltp = ltp_dict.get('ltp')
				order_obj.exitPrice = ltp
				order_obj.remark = 'Manually Squared OFF'
				if order_obj.sellQty and order_obj.sellAvg :
					order_obj.sellQty = int(order_obj.buyQty) + int(order_obj.sellQty)
					order_obj.sellAvg = float(order_obj.buyAvg) + float(order_obj.sellAvg)
				else:
					order_obj.sellQty = int(order_obj.buyQty)
					order_obj.sellAvg = float(order_obj.buyAvg)
				order_obj.save()
				if order_obj.exitPrice:
					exit_price = float(order_obj.exitPrice)
					entry_price = float(order_obj.entryPrice)
					if order_obj.fk_strategy.fk_strategy.index_type == 'EQUITY': lot_size = int(order_obj.fk_strategy.fk_strategy.lot_size) 
					else:lot_size = int(order_obj.fk_strategy.fk_strategy.lot_size)  * lot_dict.get(order_obj.fk_strategy.fk_strategy.index_type) 
					if order_obj.order_side == 'BUY': pnl = round((exit_price - entry_price )* lot_size,2)
					else: pnl = round((entry_price - exit_price) * lot_size, 2)
					if order_obj.realizedPNL :
						previous_realized_pnl = float(order_obj.realizedPNL)
						cal_pnl = pnl + previous_realized_pnl 
						order_obj.realizedPNL = cal_pnl
					else:
						order_obj.realizedPNL = pnl 
				order_obj.is_square_off = False
				order_obj.save()
				erro_text = f'PAPER ORDER SQUARE OFF ========ORDER OBJECT====> {order_obj}====>REALIZED PNL====> {order_obj.realizedPNL}=====LTP====> {ltp}'
				ErrorLog.objects.create(error=erro_text)
				break
	except:
		traceback.print_exc()
		ErrorLog.objects.create(error=traceback.format_exc())

monitor_square_off = Timeloop()
@monitor_square_off.job(interval=timedelta(seconds=1))
def monitor_square_off_positions():
	try:
		marketTm = check_market_avaibility()
		if marketTm:
			orders = Orders.objects.filter(is_square_off = True, is_square_off_thread = False,  order_mode = 'Paper', created_at__gt=prev_day_11pm)
			if orders.exists():
				for order_obj in orders:
					threading.Thread(target=square_off_procession, args=(order_obj,)).start()
					order_obj.is_square_off_thread = True
					order_obj.save()
			tsl_obj =  BreakoutPosition.objects.filter(create_dt__gt=prev_day_11pm , is_tsl_thread = True)
			if tsl_obj.exists():
				for obj in tsl_obj:
					open_order_obj = Orders.objects.filter(fk_strategy = obj, status='OPEN', fk_strategy__pos_status = 'OPEN',  created_at__gt=prev_day_11pm,is_exit = False).last()
					ltp_dict  = data_dict.get(str(obj.subscribe_token))
					if ltp_dict is not None and ltp_dict.get('ltp') is not None:
						ltp = ltp_dict.get('ltp')
						stoploss = 1
						if open_order_obj and open_order_obj.order_side == 'SELL':
							if obj.stop_loss: stoploss = float(obj.stop_loss) - float(obj.tsl)
							else: stoploss = 1
						else: stoploss = float(obj.stop_loss) + float(obj.tsl) if obj.stop_loss else 0 + float(obj.tsl) 
						obj.start_tsl_on = ltp + float(obj.tsl)
						obj.stop_loss = stoploss
						obj.is_tsl_thread = False
						obj.save()
						update_td = {
							'tr_id': obj.id,
							'stop_loss': obj.stop_loss,
						}
						async_to_sync(channel_layer.group_send)(
							"Test_Consumer",
							{
								"type": "send_live_data",
								"value": {'tsl_sl_update': update_td  }
							}
						) 
	except:
		traceback.print_exc()
		ErrorLog.objects.create(error=traceback.format_exc())

