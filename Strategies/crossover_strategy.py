import sys
sys.path.append('E:\Quanturf\Trade_board\helpers\\')
import os

import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# tradeinfo = importlib.import_module('.helpers.tradeinfo', package=".Trade_board")
# path = util.find_spec('helpers.tradeinfo',package='helpers')
# print(path.loader)
# try:
#     from helpers.tradeinfo import live_trading
# except:
from ..helpers.tradeinfo import start_trading
from ..helpers.utils import getApi
# import importlib
# from importlib import util



# **********************************************

def getApi():
    load_dotenv()

    API_KEY_ID = os.getenv('API_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
    
    api = tradeapi.REST(API_KEY_ID, SECRET_ACCESS_KEY, base_url='https://paper-api.alpaca.markets' ,api_version='v2')
    
    return api

api = getApi()



# ******************************************

def crossover_strategy():
    bar_timeframe = '1Min'
    symbol = "AAPL"
        
    data = api.get_bars(symbol, bar_timeframe, limit=200, adjustment='raw').df
    
    
    short_window = 50
    long_window = 100

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)   
    signals['positions'] = signals['signal'].diff()

    signals['signal'] = np.where(signals['signal'] == 0, 0.0, signals['signal'])
    signals['signal'] = np.where(signals['signal'] == 1, 1.0, signals['signal'])
    signals['signal'] = np.where(signals['positions'] == 0, 0.5, signals['signal'])

    start_trading(symbol, signals ,'crossover_strategy',50)

if __name__=="__main__":
    crossover_strategy()