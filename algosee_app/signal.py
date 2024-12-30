import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from datetime import datetime as dt, timedelta, time, date
from django.utils import timezone
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict
from channels.layers import get_channel_layer
import traceback
from django.template.loader import render_to_string

channel_layer = get_channel_layer()
today = date.today()
prev_day_11pm =  dt.combine(timezone.now().date() - timedelta(days=1), time(23, 0, 0, tzinfo=timezone.get_current_timezone()))

@receiver(post_save, sender=BreakoutPosition)
def TradePositions_post_save(sender, instance: BreakoutPosition, **kwargs):   
    try:
        user = instance.fk_strategy.fk_user
        trade_pos = BreakoutPosition.objects.filter(fk_strategy__fk_user=user, create_dt__gt=prev_day_11pm , pos_status__in = ['OPEN', 'REJECTED'] ).order_by('-id')
        for i in trade_pos:
            i.order_obj = Orders.objects.filter(fk_strategy = i).last()

        r_t_s_context = {'current_pos': trade_pos }
        nft_rendered = render_to_string('RenderToString/r_t_s_position.html', r_t_s_context)

        async_to_sync(channel_layer.group_send)(
            "Test_Consumer",
            {
                "type": "send_live_data",
                "value": {'page_update':nft_rendered  }
            }
        ) 
    except : ErrorLog.objects.create(error=traceback.format_exc())          

@receiver(post_save, sender=Orders)
def OrderPositions_post_save(sender, instance: Orders, **kwargs):
    try:
        user = instance.fk_strategy.fk_strategy.fk_user
        trade_pos = BreakoutPosition.objects.filter(fk_strategy__fk_user=user, create_dt__gt=prev_day_11pm , pos_status__in = ['OPEN', 'REJECTED'] ).order_by('-id')
        for i in trade_pos:
            i.order_obj = Orders.objects.filter(fk_strategy = i).last()

        r_t_s_context = {'current_pos': trade_pos }
        nft_rendered = render_to_string('RenderToString/r_t_s_position.html', r_t_s_context)

        async_to_sync(channel_layer.group_send)(
            "Test_Consumer",
            {
                "type": "send_live_data",
                "value": {'page_update':nft_rendered  }
            }
        )  
    except: ErrorLog.objects.create(error=traceback.format_exc())


@receiver(post_save, sender=TargetSl_Monitor)
def TargetSl_Monitor_post_save(sender, instance: TargetSl_Monitor, **kwargs):
    try:
        instance_data = model_to_dict(instance)
        for key, value in instance_data.items():
                if isinstance(value, (date, dt)):
                    instance_data[key] = value.isoformat()
        userMode = MyUser.objects.filter(id = instance.fk_user.id).last()
        instance_data['tradingMode'] = userMode.trading_mode
        instance_data['userId'] = userMode.id
        async_to_sync(channel_layer.group_send)(
                "Test_Consumer",
                {
                    "type": "send_live_data",
                    "value": {'overall_tsl_update':json.dumps(instance_data)}
                }
            )
    except: ErrorLog.objects.create(error=traceback.format_exc())