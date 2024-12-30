from .views import *
from .views_aj import *
from django.urls import path
from .views import * 

web_urls = [
    path('', Login),
    path('index/', index),
]

ajax_urls = [
	path('login_handler/', login_handler) , 
	path('get_strike_price/', get_strike_price) , 
    path('save-stretegy/', save_stretegy, name='save_stretegy'),
    path('square_off_position/', square_off_position,name='square_off_position'),
    path('delete_position/', delete_position,name='delete_position'),
    path('save-target-sl-other-setup/', save_target_sl_other_setup ,name='save_target_sl_other_setup'),
    path('save-target-points/', save_target_points ,name='save_target_points'),
]

urlpatterns = [*web_urls, *ajax_urls]