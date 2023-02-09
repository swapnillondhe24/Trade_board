import alpaca_trade_api as tradeapi
# from alpaca_trade_api.rest import REST,TimeFrame
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
try:
    from TradeInformation import TradeInformation
    
except:
    from helpers.TradeInformation import TradeInformation
    
import logging
from multiprocessing import Process
import multiprocessing
import time
import subprocess


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

load_dotenv()

API_KEY_ID = os.getenv('API_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')

api = tradeapi.REST(API_KEY_ID, SECRET_ACCESS_KEY, base_url='https://paper-api.alpaca.markets' ,api_version='v2')
  
trade_info = TradeInformation()

def start_dashboard():
    try:
        subprocess.run("npm start",cwd="..\dashboard\quanturf_tradeboard",shell=True)
    except:
        subprocess.run("npm start",cwd=".\dashboard\quanturf_tradeboard",shell=True)


def crossover_strategy(data):
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

    return signals


# def get_bars_data(symbol, timeframe,limit=None):
#     bars = api.get_bars(symbol, timeframe, limit=200,adjustment='raw')
    
#     df = pd.DataFrame(bars)
#     print(df.columns.values)
#     # df = df.set_index('t')
#     return df



def live_trading(symbol, strategy_func=crossover_strategy,q=None):
    bar_timeframe = '1Min'
    while True:
        barset = api.get_bars(symbol, bar_timeframe, limit=200, adjustment='raw').df
        data = barset
        signals = strategy_func(data)
        # print(signals)
        signal = signals['signal'][-1]
        
        qty = 100
        if signal == 1.0:
            # qty = int(int(api.get_account().cash) / api.get_latest_trade(symbol).price)
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='ioc'
            )
            trade_info.update_trade(symbol, order.submitted_at, qty, order.filled_avg_price)
            q.put(trade_info)
        elif signal == 0.0:
            # qty = api.get_position(symbol).qty
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='ioc'
            )
            trade_info.update_trade(symbol, api.get_last_trade(symbol).time, qty, api.get_last_trade(symbol).price)
            q.put(trade_info)
        elif signal ==0.5:
            print("Holding for now")
            trade_info.update_trade("symbol","nothing here", "qty", "api.get_last_trade(symbol).price")
            time.sleep(1)
            continue
        time.sleep(10)

def run_processes(symbol,strategy_func=crossover_strategy):
    # print("Here")
    trade_results = multiprocessing.Queue()
    
    dashboard_process = Process(target=start_dashboard)
    trading_process = Process(target=live_trading, args=(symbol, strategy_func, trade_results))

    dashboard_process.start()
    time.sleep(10)
    trading_process.start()

    while True:
        # print("running")
        trade_result = trade_results.get()
        yield trade_result
        time.sleep(2)
        
# if __name__ == '__main__':
#     while True:
#         gen = run_processes("AAPL")
#         next(gen)