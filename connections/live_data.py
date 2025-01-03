import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PavanAlgo.settings')
django.setup()

import threading
import traceback
from datetime import datetime as dt, date, timedelta, time as _time
from .truedataAPI import trudata_api
import logging, time, asyncio, json, websockets
from channels.layers import get_channel_layer
import subprocess
import requests
import pandas as pd
from algosee_app.models import *
from django.conf import settings
import time as tm
from collections import defaultdict
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

channel_layer = get_channel_layer()
SEND_TIME_INTERVAL = 0.1

check_day = date.today().weekday()
def check_market_avaibility():
	global check_day
	# if check_day >= 0 and check_day <= 4:
	# 	check_time = dt.now().time()	
	# 	if (check_time >= time(9,15) and check_time <= time(15,30)):
	# 		return True
	# return False
	return True

def format_expiry_date(date_timestamp):
    if isinstance(date_timestamp, dt):
        expiry_datetime = date_timestamp
    else:
        expiry_datetime = dt.strptime(date_timestamp, "%Y-%m-%d %H:%M:%S")
    formatted_date = expiry_datetime.strftime("%d%b%y").upper()
    return formatted_date


# FOR MASTERTRUST
def all_tokens_lst():
    try:
        nfty_symb_date = OptionExpiry.objects.filter(index='NIFTY').order_by('expiry').first()
        bnf_symb_date = OptionExpiry.objects.filter(index='BANKNIFTY').order_by('expiry').first()
        obj_eq = list(SymbolsMaster.objects.filter(trading_symbol__endswith='EQ').values_list('token', flat=True))
        filtered_data = pd.DataFrame([[1, token] for token in obj_eq], columns=['type', 'token'])
        bnf_expiry, nfty_expiry = None, None
        if nfty_symb_date:
            nfty_expiry = f'NIFTY{format_expiry_date(pd.Timestamp(nfty_symb_date.expiry)).upper()}'
        if bnf_symb_date:
            bnf_expiry = f'BANKNIFTY{format_expiry_date(pd.Timestamp(bnf_symb_date.expiry)).upper()}'

        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = pd.DataFrame(response.json()) 
        target_symbols = {"NIFTY": nfty_expiry, "BANKNIFTY": bnf_expiry}
        for symbol_name, expiry in target_symbols.items():
            if expiry:
                filtered = data[data['symbol'].str.startswith(expiry)]
                filtered = filtered[['token']]
                filtered['type'] = 2 
                filtered_data = pd.concat([filtered_data, filtered[['type', 'token']]])
                
        fixed_tokens = pd.DataFrame([[1, 26000], [1, 26009]], columns=['type', 'token'])
        filtered_data = pd.concat([filtered_data, fixed_tokens])
        return filtered_data.values.tolist()

    except Exception as e:
        print(f"Error occurred: {e}")
        return []
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def parse_symbol_info(symbol):
    if symbol.startswith("NIFTY"):
        symbol_name = "NIFTY"
        strike_price = symbol[5:-2] 
    elif symbol.startswith("BANKNIFTY"):
        symbol_name = "BANKNIFTY"
        strike_price = symbol[9:-2]
    else:
        return None, None
    return symbol_name, strike_price

data_dict_lock = threading.Lock()
data_dict = {}

def run_command():
    try:
        command = 'python manage.py runserver'
        subprocess.run(command, shell=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)



    # MASTERTRUST FEED IS ACTIVE
token_lst = all_tokens_lst()
symbol_dict = {str(token[1]): str(token[0]) for token in token_lst}
flat_token_list = [token[0] for token in token_lst]
access_token = None
data_folder = 'csv_reply_data'

def convert_string(string):
    return int.from_bytes(string, byteorder='big')

def convert(number, points):
    decimal = pow(10, points)
    return number / decimal

async def fetch_market_data():
    global data_dict
    try:
        async with websockets.connect(f'wss://masterswift-beta.mastertrust.co.in/ws/v1/feeds?token={access_token}') as websocket:
            subscribe_message = {
                "a": "subscribe", 
                "v": token_lst, 
                "m": "marketdata"
            }
            await websocket.send(json.dumps(subscribe_message))
            while True:
                response = await websocket.recv()
                await process_data(response)
    except Exception as e:
        await asyncio.sleep(2)
        threading.Thread(target=run_command).start()

async def process_data(response):
    global data_dict
    temp_dict = {}
    token = str(convert_string(response[2:6]))
    temp_dict['ltp'] = convert(convert_string(response[6:10]), 2)
    temp_dict['prev_day_close'] = convert(convert_string(response[74:78]), 2)
    temp_dict['symbol'] = token
    prev_day_close = convert(convert_string(response[74:78]), 2)
    if prev_day_close != 0:
        day_change = convert(convert_string(response[6:10]), 2) - prev_day_close
        day_change_perc = round((day_change / prev_day_close) * 100, 2)
    else:
        day_change = 0
        day_change_perc = 0
    temp_dict['change'] = day_change
    temp_dict['change_perc'] = day_change_perc
    temp_dict['market_status'] = True
    with data_dict_lock:
        data_dict[token] = temp_dict
    # await save_to_csv(token, temp_dict)
    asyncio.create_task(save_to_csv(token, temp_dict))


async def save_to_csv(token, data):
    try:
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        file_path = os.path.join(data_folder, f"{token}.csv")
        file_exists = os.path.isfile(file_path)
        timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            timestamp,
            data['ltp'],
            data['prev_day_close'],
            data['change'],
            data['change_perc'],
        ]

        # Check if timestamp already exists
        async with asyncio.Lock():
            if file_exists:
                with open(file_path, mode='r') as csv_file:
                    reader = csv.reader(csv_file)
                    existing_timestamps = {row[0] for row in reader if len(row) > 0}
                    if timestamp in existing_timestamps:
                        return

        # Write to CSV file
        async with asyncio.Lock():
            with open(file_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                if not file_exists:
                    writer.writerow(['timestamp', 'ltp', 'prev_day_close', 'change', 'change_perc'])
                writer.writerow(row)

    except Exception:
        traceback.print_exc()

async def send_data():
    while True:
        try:
            if check_market_avaibility():
                await send_data_to_consumers()
                await asyncio.sleep(SEND_TIME_INTERVAL)
        except : traceback.print_exc()

async def periodic_save():
    """Runs save-to-CSV operation every second."""
    while True:
        try:
            tasks = []
            async with data_dict_lock:
                for token, data in data_dict.items():
                    tasks.append(asyncio.create_task(save_to_csv(token, data)))
            if tasks:
                await asyncio.gather(*tasks)
            await asyncio.sleep(1)  # Delay for 1 second
        except Exception:
            traceback.print_exc()

async def send_data_to_consumers():
    try:
        await channel_layer.group_send('Test_Consumer', {
            'type': 'send_live_data',
            'value': {'live_data': json.dumps(data_dict)}
        })
    except : traceback.print_exc()

async def main():
    tasks = [fetch_market_data(), send_data()]
    await asyncio.gather(*tasks)

def run_main_loop_in_thread():
    try: asyncio.run(main())
    except : traceback.print_exc()



if AdminMaster.objects.filter(trade_mode = 'LIVE'):
    main_loop_thread = threading.Thread(target=run_main_loop_in_thread)
    main_loop_thread.start()





# closed Market ---------------

# Input directory and CSV files

input_dir = f'{settings.BASE_DIR}/csv_reply_data/' 
csv_files = [ os.path.join(input_dir, f)  for f in sorted(os.listdir(input_dir)) if f.endswith('.csv')][:100]
file_iterators = {file: iter(pd.read_csv(file).iterrows()) for file in csv_files}

ohlc_data = {
    '1s': defaultdict(lambda: {'open': None, 'high': None, 'low': None, 'close': None, 'timestamp': None}),
    '3s': defaultdict(lambda: {'open': None, 'high': None, 'low': None, 'close': None, 'timestamp': None}),
    '5s': defaultdict(lambda: {'open': None, 'high': None, 'low': None, 'close': None, 'timestamp': None}),
    '1m': defaultdict(lambda: {'open': None, 'high': None, 'low': None, 'close': None, 'timestamp': None})
}


async def send_data_consumer():
    try:
        await channel_layer.group_send(
            'Test_Consumer',
            {
                'type': 'send_live_data',
                'value': {'live_data': json.dumps(data_dict)}
            }
        )
    except Exception as e:
        print(f"Send data error: {e}")
        traceback.print_exc()

# Async Wrapper for Sync Code
def send_data_consumer_sync():
    try:
        asyncio.run(send_data_consumer())
    except Exception as e:
        print(f"Error in async wrapper: {e}")
        traceback.print_exc()

# Process CSV Files in Threads
def process_csv_file(file_name):
    try:
        while True:
            index, row = next(file_iterators[file_name])

            # Prepare data
            temp_dict = {}
            symbol = os.path.basename(file_name).replace('.csv', '')
            temp_dict['symbol'] = symbol
            temp_dict['ltp'] = row['ltp']
            temp_dict['time'] = row['timestamp']
            temp_dict['market_status'] = True

            prev_day_close = row['prev_day_close'] if 'prev_day_close' in row else 0
            if prev_day_close != 0:
                day_change = temp_dict['ltp'] - prev_day_close
                day_change_perc = round((day_change / prev_day_close) * 100, 2)
            else:
                day_change = 0
                day_change_perc = 0

            temp_dict['change'] = day_change
            temp_dict['change_perc'] = day_change_perc

            with data_dict_lock:
                data_dict[symbol] = temp_dict
            
            tm.sleep(1) 
            send_data_consumer_sync()
    except StopIteration:
        print(f"End of data for {file_name}")
    except Exception as e:
        print(f"Error processing {file_name}: {e}")
        traceback.print_exc()


# Start Threads for Parallel CSV Processing
def start_parallel_processing():
    try:
        max_workers = min(10, os.cpu_count() or 4) 
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_csv_file, file_name): file_name for file_name in csv_files}
            for future in as_completed(future_to_file):
                file_name = future_to_file[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")
                    traceback.print_exc()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


# Async Main Function
async def main():
    try:
        start_parallel_processing()  
    except Exception as e:
        print(f"Main error: {e}")
        traceback.print_exc()


# Run Async Main Loop in a Separate Thread
def run_main_loop_in_thread():
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Main loop error: {e}")
        traceback.print_exc()


if AdminMaster.objects.filter(trade_mode = 'PAPER'):
    print("---------data send------")
    main_loop_thread = threading.Thread(target=run_main_loop_in_thread)
    main_loop_thread.start()
