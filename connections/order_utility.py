from datetime import datetime as dt
import traceback
from algosee_app.models import ErrorLog, Orders, BrokerAccount

def SaveOrder(strategy, ltp, quantity, order_id, exchange, token, orderSide, orderType, product,  order_mode , symbol):
    order_obj = Orders.objects.create(fk_strategy_id = strategy, ltp=ltp, qty=quantity, buyQty = quantity, buyAvg = ltp, entryPrice= ltp,  symbol=symbol, order_id=order_id, exchange=exchange, token=token, order_side=orderSide, order_type=orderType, product=product,  order_mode=order_mode , status = 'OPEN', created_at=dt.now() , remark = 'Order placed')
    return order_obj

def CreateLiveOrder(strategy, ltp, quantity, order_id, exchange, token, orderSide, orderType, product,  order_mode , symbol, remark, status, oms_order_id):
    order_obj = Orders.objects.create(fk_strategy_id = strategy, ltp=ltp, qty=quantity, buyQty = quantity, buyAvg = ltp, entryPrice= ltp,  symbol=symbol, order_id=order_id, exchange=exchange, token=token, order_side=orderSide, order_type=orderType, product=product,  order_mode=order_mode , status = status, created_at=dt.now() , remark = remark , oms_order_id = oms_order_id)
    return order_obj

def order_monitoring(broker , order_obj, remark = None):
    from connections.mastertrust import getPositions, orderHistory
    data = getPositions(broker.client_id, broker.access_token)
    dataList = data.get('data')
    order_resp = orderHistory(broker.client_id, broker.access_token , order_obj.oms_order_id)
    try:
        if order_resp['data'][0]['status'] == "complete":
            position_dict = [item for item in dataList if item.get('token') == int(order_obj.token)]
            orderSide = order_resp['data'][0]['order_side']
            if position_dict:
                if orderSide == order_obj.order_side:
                    order_obj.entryPrice =  order_resp['data'][0]['avg_price']
                    order_obj.ltp = position_dict[0]['ltp']
                    order_obj.buyAvg = order_resp['data'][0]['avg_price']
                    order_obj.sellAvg = position_dict[0]['average_sell_price']
                    order_obj.buyQty = position_dict[0]['buy_quantity']
                    order_obj.sellQty = position_dict[0]['sell_quantity']
                    order_obj.qty = position_dict[0]['net_quantity']
                    order_obj.save()
                if orderSide != order_obj.order_side:
                    order_obj.sellAvg = order_resp['data'][0]['avg_price']
                    order_obj.buyQty = position_dict[0]['buy_quantity']
                    order_obj.sellQty = position_dict[0]['sell_quantity']
                    order_obj.qty = position_dict[0]['net_quantity']             
                    order_obj.save()
                    if position_dict[0]['net_quantity'] == 0:
                        order_obj.exitPrice = order_resp['data'][0]['avg_price']
                        order_obj.status = 'CLOSED'
                        order_obj.remark = remark
                        order_obj.save()	

        elif order_resp['data'][0]['status'] == 'rejected':
            if order_obj.status != "CLOSED":
                order_obj.remark = order_resp['data'][0]['reject_reason']
                order_obj.status = 'CLOSED'
                order_obj.save()
            if order_obj.fk_strategy.pos_status != "REJECTED":
                order_obj.fk_strategy.pos_status = 'REJECTED'
                order_obj.fk_strategy.pos_remark = 'Order has been rejected'
                order_obj.fk_strategy.save()
    except:
        ErrorLog.objects.create(error=traceback.format_exc())
        traceback.print_exc()


