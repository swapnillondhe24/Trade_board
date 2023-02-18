import alpaca_trade_api as tradeapi
# from alpaca_trade_api.rest import REST,TimeFrame
import os
import pandas as pd
import numpy as np
import logging
from multiprocessing import Process
import multiprocessing
import time
import subprocess

try:
    from TradeInformation import TradeInformation
except:
    from helpers.TradeInformation import TradeInformation
    

try:
    from utils import getApi, write_order_to_csv
except:
    from helpers.utils import getApi,write_order_to_csv

api = getApi()


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
  
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



def submit_order_with_strategy(symbol, qty, side, type, time_in_force, strategy):
    order = api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        type=type,
        time_in_force=time_in_force
    )
    filename = "../resources/"+str(strategy.__name__)
    write_order_to_csv(order,filename)
    
    return order



def live_trading(symbol, strategy_func=crossover_strategy,q=None):
    bar_timeframe = '1Min'
    while True:
        barset = api.get_bars(symbol, bar_timeframe, limit=200, adjustment='raw').df
        data = barset
        signals = strategy_func(data)
        # print(signals)
        signal = signals['signal'][-1]
        
        qty = 100
        # signal = 0.0
        if signal == 1.0:
        # if True:
            # qty = int(int(api.get_account().cash) / api.get_latest_trade(symbol).price)
            order = submit_order_with_strategy(symbol, qty, 'buy', 'market', 'gtc', strategy_func)
            # print(order)
            trade_info.update_trade(symbol, order.submitted_at, qty, order.filled_avg_price)
            q.put(trade_info)
            # break
        elif signal == 0.0:
            # qty = api.get_position(symbol).qty
            order = submit_order_with_strategy(symbol, qty, 'sell', 'market', 'gtc', strategy_func)
            trade_info.update_trade(symbol, order.submitted_at, qty, api.get_latest_trade(symbol).price)
            q.put(trade_info)
        
        elif signal ==0.5:
            # print("Holding for now")
            # trade_info.update_trade("symbol","nothing here", "qty", "api.get_last_trade(symbol).price")
            time.sleep(1)
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


# print(live_trading("AAPL"))
# if __name__ == '__main__':
#     while True:
#         gen = run_processes("AAPL")
#         next(gen)