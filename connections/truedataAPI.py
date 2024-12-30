import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PavanAlgo.settings')
django.setup()

import requests
import pandas as pd
from datetime import datetime as dt, timedelta
from django.utils import timezone
from algosee_app.models import TruedataAccount, OptionExpiry, ErrorLog, MarketFeed, LotSize, OptionData
import traceback

class TrueDataAPI:
    def __init__(self):
        self.truedata_obj = None
        self.username = None
        self.password = None
        self.port = None
        self.allsymbol = {}
        self.strikes_dict = {}
        self.nifty_update_time = MarketFeed.objects.filter(nifty_update_time = dt.now().today()).last()
        self.bnf_update_time = MarketFeed.objects.filter(bnf_update_time = dt.now().today()).last()
        self.map_symbol_token = {'NIFTY BANK': 26009 , 'NIFTY 50': 26000}
        self.token_symbol_map = {26000: 'NIFTY 50', 26009: 'NIFTY BANK'}
        self.INTIALIZE_STRIKES()
        self.SAVE_STRIKES('NIFTY')
        self.SAVE_STRIKES('BANKNIFTY')

    def NIFTYDYO_MT(self):
        try: return self.get_mt_data('NSE_INDICES', 26000,  'nifty_open_price', 'nifty_update_time')
        except:
            traceback.print_exc()
            return None

    def BANKNIFTYDYO_MT(self):
        try: return self.get_mt_data('NSE_INDICES', 26009, 'bnf_open_price', 'bnf_update_time')
        except:
            traceback.print_exc()
            return None

    def get_mt_data(self, exchange, token ,field_name, field_update_time):
        error_text = f'START SAVING {token} OPEN PRICE USING MASTERTRUST'
        ErrorLog.objects.create(error=error_text)

        import time
        to_tf = int(time.time())  
        from_tf = to_tf - (7 * 24 * 60 * 60) 

        url = f'https://masterswift-beta.mastertrust.co.in/api/v1/charts/tdv?exchange={exchange}&token={token}&candletype=3&starttime={from_tf}&endtime={to_tf}'
        response = requests.get(url)
        response = response.json()
        if response.get('status') == 'success' and 'data' in response and isinstance(response['data'], dict) and 'candles' in response['data'] and isinstance(response['data']['candles'], list) and len(response['data']['candles']) > 0:
            data = response['data']['candles'][-1]
            field_value = {field_name: data[1]}
            field_time = {field_update_time: dt.now().today()}
            if not MarketFeed.objects.filter(**field_value, **field_time).exists():
                MarketFeed.objects.update(**field_value, **field_time)
            error_text = f'SAVING {token} OPEN PRICE USING MASTERTRUST COMPLETED'
            ErrorLog.objects.create(error=error_text)
            return data[1]
        return None

    def INTIALIZE_STRIKES(self):
        
        try:
            error_text = f'MASTERTRUST CONTRACT API CALLED STARTED'
            ErrorLog.objects.create(error=error_text)
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
            self.strikes_dict =  token_df
            error_text = f'MASTERTRUST CONTRACT API CALLED ENDED'
            ErrorLog.objects.create(error=error_text)
            return token_df
        except Exception as e:
            error_text = f'MASTERTRUST CONTRACT API THORWS ERROR {traceback.format_exc()}'
            ErrorLog.objects.create(error=error_text)
            traceback.print_exc()
            return {}
    
    @staticmethod
    def round_down_to_nearest(value, spot):
        if spot == 'NIFTY':
            val = ((value + 25) // 100) * 100
        else:
            val = ((value + 50) // 100) * 100
        return val
        
    def SAVE_STRIKES(self, index):
        try:
            error_text = f'START SAVING STRIKE PRICE FOR {index}'
            ErrorLog.objects.create(error=error_text)
            lot_dict = {
                'NIFTY' : LotSize.objects.filter(index_name = 'NIFTY').last().lot_size,
                'BANKNIFTY' : LotSize.objects.filter(index_name = 'BANKNIFTY').last().lot_size
            }

            nifty_val = self.NIFTYDYO_MT()
            bnf_val = self.BANKNIFTYDYO_MT()
            expiry_obj = OptionExpiry.objects.filter(index = index).first()

            index_ltp = nifty_val if index == 'NIFTY' else bnf_val
            self.strikes_dict.rename(columns={'code': 'token'}, inplace=True)
            df = self.strikes_dict
            current_expiry = df[(df['exchange_code'] == 2) & (df['symbol'].str.startswith(index)) & (df['lotSize'] == str(lot_dict[index]))].sort_values(by=['expiry']).iloc[0]['expiry']
            nifty_df_new = df[df['expiry'] == current_expiry]
            nifty_df_new['strike'] = nifty_df_new['strike'].astype(float)
            nifty_df_new = nifty_df_new.sort_values(by='strike').reset_index(drop=True)
            
            if index_ltp:
                new_index_ltp = float(index_ltp)
                selected_strike = self.round_down_to_nearest(float(index_ltp), index)
                nifty_df_new['diff'] = abs(nifty_df_new['strike'] - new_index_ltp)
                nearest_idx = nifty_df_new['diff'].idxmin()
                start_idx = max(nearest_idx - 30, 0)
                end_idx = min(nearest_idx + 30, len(nifty_df_new) - 1)
                result_df = nifty_df_new.iloc[start_idx:end_idx + 1]
                result_df = result_df.drop(columns=['diff'])
                result_df['strike_divided'] = result_df['strike']
                result_df['strike'] = result_df.apply(lambda row: f"{int(row['strike_divided'])}", axis=1)
                result_df['new_strike'] = result_df.apply(lambda row: f"{int(row['strike_divided'])}{row['symbol'][-2:]}", axis=1)
                result_df = result_df[['strike', 'token', 'new_strike']]
                result_dict = result_df.to_dict(orient='records')
                unique_dict = sorted({(item['strike'], item['token'], item['new_strike']) for item in result_dict})
                unique_strikes = sorted({item['strike'] for item in result_dict})
                update_unique_dict = [{"strike": strike, "token": token, "new_strike" : new_strike } for strike, token, new_strike in unique_dict]
                obj_data = OptionData.objects.last()
                if obj_data  :
                        if index == 'NIFTY':
                            # if obj_data.updated_dt != dt.today():
                                obj_data.nifty_unique_strikes = unique_strikes
                                obj_data.nifty_update_unique_dict = update_unique_dict
                                obj_data.nifty_selected_strike = selected_strike
                        else:
                            # if obj_data.updated_dt != dt.today():
                                obj_data.bnf_unique_strikes = unique_strikes
                                obj_data.bnf_update_unique_dict = update_unique_dict
                                obj_data.bnf_selected_strike = selected_strike
                        # print('---------', index)
                        # print(unique_strikes)
                        # print(update_unique_dict)
                        # print(selected_strike)
                        obj_data.updated_dt = dt.today()
                        obj_data.save()
                else:
                    if index == 'NIFTY':
                        OptionData.objects.create(nifty_unique_strikes = unique_strikes, nifty_update_unique_dict = update_unique_dict, nifty_selected_strike = selected_strike, updated_dt = dt.today())
                    else:
                        OptionData.objects.create(bnf_unique_strikes = unique_strikes, bnf_update_unique_dict = update_unique_dict, bnf_selected_strike = selected_strike, updated_dt = dt.today())
                error_text = f'STRIKE PRICE SAVING COMPLETED FOR {index}'
                ErrorLog.objects.create(error=error_text)
                return True
            else:
                error_text = f'ERROR WHEN SAVING STRIKE PRICE {index_ltp}'
                ErrorLog.objects.create(error=error_text)
                return False
        except:
            error_text = f'SAVING STRIKE PRICE FUNC THORW ERROR  {traceback.format_exc()}'
            ErrorLog.objects.create(error=error_text)
            traceback.print_exc()
            return False


trudata_api = TrueDataAPI()

