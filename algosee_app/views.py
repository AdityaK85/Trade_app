from datetime import datetime as dt, timedelta, time
from django.utils import timezone
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .models import *
from django.views.decorators.cache import cache_control
from Project_utilty.decorators import *
# Create your views here.
def Login(request):
    return render(request, 'login.html')

def redirect_on_login(request):
    return redirect('/admin_panel/Login/')

def check_expiries():
    OptionExpiry.objects.filter(expiry__lt=dt.now().date()).delete()
    return True

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@handle_client_page_exception
def index(request, user):
    check_expiries()
    today = timezone.now().date()

    market_ltp = MarketFeed.objects.last()
    obj_eq = SymbolsMaster.objects.filter(trading_symbol__endswith='EQ').order_by('symbol')
    remaining_days = 0
    prev_day_11pm = dt.combine(timezone.now().date() - timedelta(days=1), time(23, 0, 0, tzinfo=timezone.get_current_timezone()))
    mastertrust_obj = BrokerAccount.objects.filter(fk_user=user).last()
    targ_sl = TargetSl_Monitor.objects.filter(fk_user=user).last()

    trade_pos = BreakoutPosition.objects.filter(fk_strategy__fk_user=user, create_dt__gt=prev_day_11pm , pos_status__in = ['OPEN', 'REJECTED'] ).order_by('-id')
           
    for i in trade_pos:
        i.order_obj = Orders.objects.filter(fk_strategy = i).last()

    r_t_s_context = {'current_pos': trade_pos }
    nft_rendered = render_to_string('RenderToString/r_t_s_position.html', r_t_s_context)

    context = {
        'mastertrust_obj': mastertrust_obj,
        'user' : user , 
        'nft_rendered' : nft_rendered , 
        'targ_sl': targ_sl , 
        'trading_mode':user.trading_mode ,
        'remaining_days': remaining_days, 
        'market_ltp': market_ltp,
        'obj_eq': obj_eq
    }
    return render(request, 'index.html', context)


def technical_chart(request):
    return render(request, 'chart.html')

import requests
import pandas as pd
import json

# # URL to fetch the data
# url = 'https://history.truedata.in/getticks?symbol=NIFTY25010223500CE&bidask=1&from=241231T09:15:00&to=241231T15:30:00&response=JSON'
# token = 'Bearer yLKUdeGXKYh_Z_IO2E4EViq0pt1sMwlyLCBePhwV7YRY1Qk_s6qsbUOD2hRjC4RXqbrdS5fs2ZwBBhCnKnLGErwX2uwrr9Yn1OpBPRb7P7pcgO2ggalwz9zScWB2DbYvAqB7YLx1SHbHC9k_x4cIs1p6rN9KpDebuieilkUihKRI63Prg8q3imz5jNR3xMICZRAxLoIE-eZSfY7aee8F7YcjvIBjBwNdz7JWq4bh4bOnuBoqQrwDn7ZIr9TDw1hhrqdD4rYU4JxWJhznjZyqjg'


# # Output CSV filename
# output_file = '52497.csv'

# try:
#     # Make a GET request to fetch the data
#     headers = {'Authorization': token}
#     response = requests.get(url, headers=headers)

#     # Parse the JSON response
#     data = response.json()

#     # Check if data exists in response
#     if 'Records' not in data or len(data['Records']) == 0:
#         print("No data available in the response.")
#     else:
#         # Extract records
#         records = data['Records']

#         # Convert records to DataFrame
#         df = pd.DataFrame(records, columns=['timestamp', 'ltp', 'bid', 'ask', 'bidQty', 'askQty', 'volume', 'unknown'])

#         # Convert timestamp to datetime
#         df['timestamp'] = pd.to_datetime(df['timestamp'])

#         # Save DataFrame to CSV
#         df.to_csv(output_file, index=False)
#         print(f"Data saved successfully to {output_file}")

# except requests.exceptions.RequestException as e:
#     print(f"Error fetching data: {e}")
# except json.JSONDecodeError as e:
#     print(f"Error decoding JSON: {e}")
# except Exception as e:
#     print(f"An error occurred: {e}")