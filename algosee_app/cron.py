import subprocess
from algosee_app.models import *
import traceback
import datetime as dt
import time
from django.utils import timezone
import requests
from django.conf import settings

def run_restart_command():
    try:
        ErrorLog.objects.create(error = '+++++++++++++++RESTART CMD CALLED++++++++++++++')
        command = settings.RESTART_SERVER_CMD
        subprocess.run(command, shell=True)
        ErrorLog.objects.create(error = '+++++++++++++++RESTART CMD CALLED COMPLETED++++++++++++++')
        return True
    except :
        traceback.print_exc()
        ErrorLog.objects.create(error = traceback.format_exc())
        return False
    
def clear_token():
    try:
        ErrorLog.objects.create(error = '+++++++++++++++CLEAR TOKENS FUNC START CALLED++++++++++++++')
        BrokerAccount.objects.all().update(access_token = None)
        ErrorLog.objects.create(error = '+++++++++++++++CLEAR TOKENS FUNC END CALLED++++++++++++++')
    except:
        ErrorLog(error = traceback.format_exc())
        
def clear_1week_before_errorlog():
    try:
        ErrorLog.objects.create(error = '+++++++++++++++CLEAR 2 DAY AGO ERRORS FUNC START CALLED++++++++++++++')
        seven_days_ago = timezone.now() - dt.timedelta(days=2)
        while True:
            ids = list(ErrorLog.objects.filter(created_dt__lt=seven_days_ago).values_list('id', flat=True)[:1000])
            if not ids:
                break
            ErrorLog.objects.filter(id__in=ids).delete()
        ErrorLog.objects.create(error = '+++++++++++++++CLEAR 2 DAY AGO ERRORS FUNC END CALLED++++++++++++++')
    except:
        traceback.print_exc()
        ErrorLog(error = traceback.format_exc())

def update_bnf_expiry():
    max_retries = 5 
    retry_delay = 2
    try:
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE BANKNIFTY EXPIRY FUNC START CALLED++++++++++++++')
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Referer': 'https://www.nseindia.com/',
        }
        for attempt in range(max_retries):
            try:
                print("000----")
                with requests.Session() as session:
                    response = session.get(url, headers=headers, timeout=5)
                    data = response.json()
                    expiry_dates = data['records']['expiryDates']
                    if expiry_dates :
                        OptionExpiry.objects.filter(index="BANKNIFTY").delete()
                    for expiry_str in expiry_dates:
                        expiry_date = dt.datetime.strptime(expiry_str, '%d-%b-%Y').date()
                        if not OptionExpiry.objects.filter(index="BANKNIFTY", expiry=expiry_date).exists():
                            option_expiry = OptionExpiry(index="BANKNIFTY", expiry=expiry_date)
                            option_expiry.save() 
                            print('000BANKNIFTY')
                    break
            except: 
                ErrorLog.objects.create(error = traceback.format_exc())
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE BANKNIFTY EXPIRY FUNC END CALLED++++++++++++++')
    except :
        ErrorLog.objects.create(error = traceback.format_exc())
    

def update_nifty_expiry():
    try:
        max_retries = 5 
        retry_delay = 2
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE NIFTY EXPIRY FUNC START CALLED++++++++++++++')
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'application/json',
            'Referer': 'https://www.nseindia.com/'
        }
        for attempt in range(max_retries):
            try:
                with requests.Session() as session:
                    response = session.get(url, headers=headers, timeout=5)
                    data = response.json()
                    expiry_dates = data['records']['expiryDates']
                    if expiry_dates :
                        OptionExpiry.objects.filter(index="NIFTY").delete()
                    for expiry_str in expiry_dates:
                        expiry_date = dt.datetime.strptime(expiry_str, '%d-%b-%Y').date()
                        if not OptionExpiry.objects.filter(index="NIFTY", expiry=expiry_date).exists():
                            option_expiry = OptionExpiry(index="NIFTY", expiry=expiry_date)
                            option_expiry.save()
                    break 
            except:
                ErrorLog.objects.create(error = traceback.format_exc())
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE NIFTY EXPIRY FUNC END CALLED++++++++++++++')
    except :
        ErrorLog.objects.create(error = traceback.format_exc())
    


def update_instrument_token():
    try:
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE INSTRUMENT TOKEN FUNC START CALLED++++++++++++++')
        url = f'{settings.MASTERTRUST_BASE_URL}/api/v2/contracts.json?exchanges=NFO'
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.request("GET", url, headers=headers)
        json_response = response.json() 
        if 'NSE-OPT' in json_response:
            for i in json_response['NSE-OPT']:
                try:
                    symbol = i['symbol']
                    if not SymbolsMaster.objects.filter(token=i['code']).exists() and ( symbol.startswith("NIFTY") or symbol.startswith("BANKNIFTY")):
                        SymbolsMaster.objects.create(token=i['code'], symbol=i['symbol'], expiry=i['expiry'], exchange_code=i['exchange_code'], exchange=i['exchange'], trading_symbol=i['trading_symbol'], company=i['company'])
                    
                except Exception as e:
                    print(f"Error creating SymbolsMaster object: {str(e)}")
                    traceback.print_exc()
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE INSTRUMENT TOKEN FUNC END CALLED++++++++++++++')
    except:
        print(str(traceback.format_exc()))


def check_30days_validation():
    try:
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE 30 DAYS VALIDATION FUNC START CALLED++++++++++++++')
        today = timezone.now().date()
        MyUser.objects.filter(expired_from__lt=today).update(trading_mode = 'Live')
        ErrorLog.objects.create(error = '+++++++++++++++UPDATE 30 DAYS VALIDATION FUNC START CALLED++++++++++++++')
        return True
    except:
        traceback.print_exc()
        return False
    

def clearTodaysCandles():
    try:
        today = timezone.now().date()
        while True:
            ids = list(CandleData.objects.filter(created_dt__date=today).values_list('id', flat=True)[:1000])
            if not ids:
                break
            CandleData.objects.filter(id__in=ids).delete()
        ErrorLog(error = 'TODAYS CANDLE DATA CLEARED CRON DONE')
    except:
        traceback.print_exc()
        return False
    
def clear_2day_before_paperorder():
    try:
        ErrorLog.objects.create(error = '+++++++++++++++CLEAR 2 DAYS BEFORE PAPER ORDER FUNC START CALLED++++++++++++++')
        two_days_ago = timezone.now() - dt.timedelta(days=2)
        while True:
            ids = list(BreakoutStrategy.objects.filter(create_dt__lt=two_days_ago, trading_mode = 'Paper').values_list('id', flat=True)[:1000])
            if not ids:
                break
            BreakoutStrategy.objects.filter(id__in=ids).delete()
        ErrorLog.objects.create(error = '+++++++++++++++CLEAR 2 DAYS BEFORE PAPER ORDER FUNC END CALLED++++++++++++++')
    except:
        traceback.print_exc()
        ErrorLog(error = traceback.format_exc())

