from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import MyCustomManager
import datetime

# Create your models here.

class AdminMaster(models.Model):
    username = models.CharField(max_length=200 , null=True  , blank=True)
    password = models.CharField(max_length=200 , null=True  , blank=True)
    trade_mode = models.CharField(max_length=200 , null=True  , blank=True, default='LIVE')  # PAPER AFTER 3 : 30
    




#### custom user details table
class MyUser(AbstractBaseUser,PermissionsMixin):
    name = models.CharField(max_length=300, blank=True,null=True)
    email = models.EmailField(max_length=300, unique=True,blank=True,null=True)
    password = models.CharField(max_length=200,blank=True,null=True)
    mobile_no = models.CharField(max_length= 100 , blank= True , null=  True)
    account_status = models.CharField(max_length= 100 , default= "Inactive") # Active , Inactive , Blocked
    user_type = models.CharField(max_length= 100 , blank= True ,null= True)
    expired_from = models.DateField(blank= True , null= True )
    created_date = models.DateTimeField(blank= True , null= True )
    is_staff = models.BooleanField(default=False)
    trading_mode = models.CharField(max_length=300 , default='Paper', null=True , blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyCustomManager()
    def __str__(self):
        return  f'Userobject: {str(self.id)} '



class BrokerAccount(models.Model):
    fk_user = models.ForeignKey(MyUser, on_delete=models.CASCADE , blank=True , null=True)
    client_id = models.CharField(max_length=50 , null=True, blank=True)
    app_password = models.CharField(max_length=50 , null=True, blank=True)
    app_scret = models.CharField(max_length=500 , null=True, blank=True)
    app_id = models.CharField(max_length=50 , null=True, blank=True)
    app_totp = models.CharField(max_length=50 , null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    is_login = models.BooleanField(default=False)
    created_dt =  models.DateTimeField(blank=True , null= True)


class ErrorLog(models.Model):
    fk_user = models.ForeignKey(MyUser, on_delete=models.CASCADE , blank=True , null=True)
    error = models.TextField(null=True , blank=True)
    created_dt = models.DateTimeField(default= datetime.datetime.now(), blank=True , null= True)



class BreakoutStrategy(models.Model):
    fk_user = models.ForeignKey(MyUser, on_delete=models.CASCADE , blank=True , null=True)
    strategy = models.CharField(max_length=300 , null=True , blank=True)
    index_type = models.CharField(max_length=300 , blank=True , null= True)
    lot_size = models.CharField(max_length=300 , blank=True , null= True)
    breakout_candle = models.CharField(max_length=300 , null=True , blank=True)
    time_frame = models.CharField(max_length=300 , null=True , blank=True)
    breakout_on = models.CharField(max_length=300 , blank=True , null= True)
    strike_round_up = models.CharField(max_length=300 , blank=True , null= True)

    segment = models.CharField(max_length=300 , null=True , blank=True)
    tradingSymbol = models.CharField(max_length=300 , null=True , blank=True)


    exchange = models.CharField(max_length=300 , null=True , blank=True)
    token  = models.CharField(max_length=300 , null=True , blank=True)
    open  = models.CharField(max_length=300 , null=True , blank=True)
    high  = models.CharField(max_length=300 , null=True , blank=True)
    low  = models.CharField(max_length=300 , null=True , blank=True)
    close  = models.CharField(max_length=300 , null=True , blank=True)

    strike_with_round_up_1  = models.CharField(max_length=300 , null=True , blank=True)
    strike_with_round_up_2  = models.CharField(max_length=300 , null=True , blank=True)
    strike_round_1  = models.CharField(max_length=300 , null=True , blank=True)
    strike_round_2  = models.CharField(max_length=300 , null=True , blank=True)
    option_type  = models.CharField(max_length=300 , null=True , blank=True)


    subscribe_token  = models.CharField(max_length=300 , null=True , blank=True)
    expiry_dt = models.DateField( null=True , blank=True)
    
    is_closed = models.BooleanField(default=False)
    trading_mode = models.CharField(max_length=300 , null=True , blank=True, default='Paper')
    create_dt = models.DateTimeField( null=True , blank=True)  

    # def __str__(self):
    #     return  f'Userobject: {str(self.id)}'


class BreakoutPosition(models.Model):
    fk_strategy = models.ForeignKey(BreakoutStrategy, on_delete=models.CASCADE , blank=True , null=True)
    order_on = models.CharField(max_length=300 , null=True , blank=True)
    set_order_side = models.CharField(max_length=300 , null=True , blank=True)
    tradingSymbol = models.CharField(max_length=300 , null=True , blank=True)
    high_price  = models.CharField(max_length=300 , null=True , blank=True)
    low_price  = models.CharField(max_length=300 , null=True , blank=True)
    strike_round  = models.CharField(max_length=300 , null=True , blank=True)
    option_type  = models.CharField(max_length=300 , null=True , blank=True)
    subscribe_token  = models.CharField(max_length=300 , null=True , blank=True)

    partial_exit = models.CharField(max_length=30, null=True, blank=True)
    partial_target = models.FloatField(blank=True, null=True)
    stop_loss = models.FloatField(blank=True, null=True)
    full_target = models.FloatField(blank=True, null=True)
    max_profit = models.FloatField(blank=True, null=True)
    max_loss = models.FloatField(blank=True, null=True)
    is_tsl_thread = models.BooleanField(default=False)
    tsl = models.FloatField(blank=True, null=True)
    start_tsl_on = models.FloatField(blank=True, null=True)

    pos_status = models.CharField(max_length=300 , null=True , blank=True)  # REMOVED / OPEN 
    pos_remark = models.CharField(max_length=300 , null=True , blank=True)  # REMOVED BY USER / AUTO REMOVE BY SYSTEM ( OVER ALL STOP LOSS HIT / OVER ALL TARGE HIT )
    thread_flag = models.BooleanField(default=True)
    monitoring_flag = models.BooleanField(default=True)
    market_excuted = models.BooleanField(default=False)
    create_dt = models.DateTimeField( null=True , blank=True)


class TargetSl_Monitor(models.Model):
    fk_user = models.ForeignKey(MyUser, on_delete=models.CASCADE , blank=True , null=True)
    # For Test Target & sl
    target = models.FloatField( null=True,blank=True)
    sl = models.FloatField( null=True,blank=True)
    remark = models.TextField(null=True , blank=True)

    # For live Target & sl
    live_target = models.FloatField( null=True,blank=True)
    live_sl = models.FloatField( null=True,blank=True)
    live_remark = models.TextField(null=True , blank=True)

    # Target Points
    nfty_target_points = models.FloatField( null=True,blank=True)
    bnf_target_points = models.FloatField( null=True,blank=True)
    equity_target_points = models.FloatField( null=True,blank=True)
    create_dt =  models.DateTimeField(blank=True , null= True)


class TradingMode(models.Model):
    fk_user = models.ForeignKey(MyUser, on_delete=models.CASCADE , blank=True , null=True)
    mode = models.BooleanField()


class Orders(models.Model):
    order_mode = models.CharField(max_length=10, null=True, blank=True)    # Paper/Live
    fk_strategy = models.ForeignKey(BreakoutPosition, on_delete=models.CASCADE, null=True, blank=True)
    ltp = models.FloatField(null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)
    token = models.IntegerField(null=True, blank=True)
    order_id = models.CharField(max_length=230, null=True, blank=True)
    oms_order_id = models.CharField(max_length=230, null=True, blank=True)
    order_side = models.CharField(max_length=10, null=True, blank=True)
    product = models.CharField(max_length=10, null=True, blank=True)
    exchange = models.CharField(max_length=10, null=True, blank=True)
    order_type = models.CharField(max_length=10, null=True, blank=True)
    symbol = models.CharField(max_length=30, null=True, blank=True)
    buyQty = models.IntegerField(blank=True, null=True)
    buyAvg = models.FloatField(blank=True, null=True)
    sellQty = models.IntegerField(blank=True, null=True)
    sellAvg = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField()
    status = models.CharField(max_length=20)    # Open/Closed
    entryPrice = models.FloatField(null=True, blank=True)
    exitPrice = models.FloatField(null=True, blank=True)
    exit_at = models.DateTimeField(null=True, blank=True)
    realizedMTM = models.FloatField(blank=True, null=True)
    realizedPNL = models.FloatField(blank=True, null=True)
    remark = models.TextField(null=True, blank=True)
    is_exit = models.BooleanField(default=False)
    is_square_off = models.BooleanField(default=False)
    is_square_off_thread = models.BooleanField(default=False)
    currentQty = models.IntegerField(blank=True, null=True)


class ResponseLog(models.Model):
    response = models.TextField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now=True)

class LinkMaster(models.Model):
    link = models.TextField(blank=True,null=True)
    sequence = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)


class SymbolsMaster(models.Model):
    trading_symbol = models.CharField(max_length=250, null=True, blank=True)
    symbol = models.CharField(max_length=250, null=True, blank=True)
    expiry = models.IntegerField(null=True , blank=True)
    exchange_code = models.IntegerField(null=True , blank=True)
    exchange = models.CharField(max_length=250, null=True, blank=True)
    token = models.IntegerField(null=True , blank=True)
    company = models.CharField(max_length=250, null=True, blank=True)


class OptionExpiry(models.Model):
    index = models.CharField(max_length=250, null=True, blank=True)
    expiry = models.DateField(null=True, blank=True)
    created_dt = models.DateTimeField(default= datetime.datetime.now(), blank=True , null= True)


class SubscriptionPrice(models.Model):
    amount = models.FloatField(null=True, blank=True)

class LotSize(models.Model):
    index_name = models.CharField(max_length=250, null=True, blank=True)
    lot_size = models.IntegerField(null=True , blank=True)


class CandleData(models.Model):
    exchange = models.CharField( max_length=250, null=True, blank=True)
    token = models.CharField( max_length=250, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField()
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    created_dt = models.DateTimeField(default= datetime.datetime.now(), blank=True , null= True)


class TruedataAccount(models.Model):
    username = models.CharField(max_length=300, blank=True, null=True)
    password = models.CharField(max_length=300, blank=True, null=True)
    port = models.CharField(max_length=300, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    token_expiry_time = models.DateTimeField(null=True, blank=True)


class MarketFeed(models.Model):
    market_data = models.CharField(max_length=300, blank=True, null=True , default='MASTERTRUST')   # MASTERTRUST / TRUEDATA
    # OPENED PRICE
    nifty_open_price = models.FloatField(null=True, blank=True)
    bnf_open_price = models.FloatField(null=True, blank=True)
    nifty_update_time = models.DateField(null=True, blank=True)
    bnf_update_time = models.DateField(null=True, blank=True)
    # CLOSED PRICE
    prev_nifty_closed_price = models.FloatField(null=True, blank=True)
    prev_bnf_closed_price = models.FloatField(null=True, blank=True)
    prev_nifty_changed = models.FloatField(null=True, blank=True)
    prev_bnf_changed = models.FloatField(null=True, blank=True)
    prev_nifty_update_time = models.DateField(null=True, blank=True)
    prev_bnf_update_time = models.DateField(null=True, blank=True)
    # CREATED DATE
    created_dt = models.DateTimeField(default= datetime.datetime.now(), blank=True , null= True)


class OptionData(models.Model):
    bnf_unique_strikes = models.JSONField(blank=True , null= True)
    bnf_update_unique_dict = models.JSONField(blank=True , null= True)
    bnf_selected_strike = models.JSONField(blank=True , null= True)

    nifty_unique_strikes = models.JSONField(blank=True , null= True)
    nifty_update_unique_dict = models.JSONField(blank=True , null= True)
    nifty_selected_strike = models.JSONField(blank=True , null= True)
    updated_dt = models.DateField( blank=True , null= True)