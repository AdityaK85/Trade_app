from django.contrib import admin
from algosee_app.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
admin.site.site_header = "TradeIQ Admin"
admin.site.site_title = "TradeIQ Admin Portal"
admin.site.index_title = "Welcome to TradeIQ"
# Register your models here.


class MyUserAdmin(BaseUserAdmin):
    fieldsets = (
    (None, {'fields': ('id', 'name', 'email', 'password','user_type', 'expired_from', 'created_date', 'trading_mode',  'is_staff','mobile_no','account_status')}),
        ('Permissions', {'fields': (
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('name','email', 'password1', 'password2')
            }
        ),
    )
    list_display = ('id', 'name', 'email','mobile_no' ,'account_status' , 'trading_mode' ,  'expired_from', 'is_staff')
    readonly_fields = ('id',)
    list_filter = ( 'groups',)
    search_fields = ('email',)
    ordering = ('-id',)
    filter_horizontal = ('groups', 'user_permissions',)
admin.site.register(MyUser, MyUserAdmin)


class AdminMasterAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'password')
admin.site.register(AdminMaster, AdminMasterAdmin)

class BrokerAccountAdmin(admin.ModelAdmin):
    list_display = ('id','fk_user', 'client_id','app_id', 'created_dt')
admin.site.register(BrokerAccount, BrokerAccountAdmin)

class TargetSl_MonitorAdmin(admin.ModelAdmin):
    list_display = ('id','fk_user', 'target','sl', 'remark', 'live_target', 'live_sl', 'live_remark', 'create_dt')
admin.site.register(TargetSl_Monitor, TargetSl_MonitorAdmin)

class BreakoutStrategyAdmin(admin.ModelAdmin):
    list_display = ('id', 'trading_mode', 'fk_user',  'index_type', 'strategy','lot_size', 'breakout_candle','time_frame', 'breakout_on','strike_round_up', 'segment', 'tradingSymbol', 'exchange', 'token', 'open', 'high', 'low', 'close', 'strike_with_round_up_1', 'strike_with_round_up_2' , 'strike_round_1','strike_round_2', 'option_type', 'subscribe_token', 'expiry_dt', 'is_closed',  'create_dt',)
admin.site.register(BreakoutStrategy, BreakoutStrategyAdmin)


class BreakoutPositionAdmin(admin.ModelAdmin):
    list_display = ('id','fk_strategy', 'order_on', 'tradingSymbol', 'strike_round', 'option_type', 'high_price', 'low_price', 'tsl', 'start_tsl_on', 'subscribe_token', 'partial_exit', 'partial_target', 'stop_loss', 'full_target', 'thread_flag', 'monitoring_flag', 'pos_status', 'pos_remark', 'create_dt')
admin.site.register(BreakoutPosition, BreakoutPositionAdmin)

class TradingModeAdmin(admin.ModelAdmin):
    list_display = ('id','fk_user', 'mode')
admin.site.register(TradingMode, TradingModeAdmin)

class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id','fk_user', 'error','created_dt')
admin.site.register(ErrorLog, ErrorLogAdmin)

class ResponseLogAdmin(admin.ModelAdmin):
    list_display = ('id','response', 'created_date')
admin.site.register(ResponseLog, ResponseLogAdmin)

class OptionExpiryAdmin(admin.ModelAdmin):
    list_display = ('id','index', 'expiry')
admin.site.register(OptionExpiry, OptionExpiryAdmin)

class LinkMasterAdmin(admin.ModelAdmin):
    list_display = ('id','link', 'sequence', 'created_date')
admin.site.register(LinkMaster, LinkMasterAdmin)

class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ('id','amount')
admin.site.register(SubscriptionPrice, SubscriptionPriceAdmin)

class SymbolsMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'trading_symbol', 'symbol', 'expiry', 'exchange_code', 'exchange', 'company', 'token')
    search_fields = ('trading_symbol', 'symbol', 'token')
    ordering = ('-id',)
admin.site.register(SymbolsMaster, SymbolsMasterAdmin)

class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_mode', 'fk_strategy', 'ltp', 'qty', 'token', 'order_id', 'order_side', 'symbol', 'buyQty' , 'buyAvg', 'sellQty','sellAvg', 'currentQty', 'created_at', 'status','exitPrice', 'exit_at')
admin.site.register(Orders, OrdersAdmin)

class LotSizeAdmin(admin.ModelAdmin):
    list_display = ('id','index_name', 'lot_size')
admin.site.register(LotSize, LotSizeAdmin)

class CandleDataAdmin(admin.ModelAdmin):
    list_display = ('id','exchange', 'token', 'duration', 'date', 'open', 'high','low', 'close', 'created_dt')
admin.site.register(CandleData, CandleDataAdmin)

class TruedataAccountAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'password', 'port')
admin.site.register(TruedataAccount, TruedataAccountAdmin)

class MarketFeedAdmin(admin.ModelAdmin):
    list_display = ('id','market_data', 'nifty_open_price', 'nifty_update_time', 'bnf_open_price', 'bnf_update_time')
admin.site.register(MarketFeed, MarketFeedAdmin)

class OptionDataAdmin(admin.ModelAdmin):
    list_display = ('id','nifty_unique_strikes', 'nifty_update_unique_dict', 'nifty_selected_strike', 'bnf_unique_strikes', 'bnf_update_unique_dict', 'bnf_selected_strike', 'updated_dt')
admin.site.register(OptionData, OptionDataAdmin)