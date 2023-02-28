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
    from  helpers.utils import getApi,write_order_to_csv

api = getApi()


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
  
trade_info = TradeInformation()


def start_dashboard():
    try:
        subprocess.run("npm start",cwd=".\Trade_board\dashboard\quanturf_tradeboard",shell=True)
    except ImportError:
        subprocess.run("npm start",cwd=".\Trade_board\dashboard\quanturf_tradeboard",shell=True)
    except KeyboardInterrupt:
        exit(0)

def start_backend():
    try:
        subprocess.run("python trading.py",cwd="./Trade_board",shell=True)
    except ImportError:
        subprocess.run("python trading.py",cwd="./Trade_board",shell=True)
    except KeyboardInterrupt:
        exit(0)




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



def live_trading(symbol, signals,strategy_func,qty = 100,q=None):
    
    while True:
        signals
        # print(signals)
        signal = signals['signal'][-1]
        
        
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


def start_trading(symbol, signals,strategy_func,qty = 100):
    # print("Here")
    try:
        trade_results = multiprocessing.Queue()

        dashboard_process = Process(target=start_dashboard)

        backend_process = Process(target=start_backend)

        trading_process = Process(target=live_trading, args=(symbol, signals,strategy_func,qty, trade_results))


        trading_process.start()
        print("running trading")
        time.sleep(5)
        dashboard_process.start()
        time.sleep(10)    
        print("running dashboard")
        backend_process.start()
        time.sleep(10)

        backend_process.join()
        dashboard_process.join()
        trading_process.join()
    except KeyboardInterrupt:
        dashboard_process.kill()
        backend_process.kill()
        trading_process.kill()
        
        print("bye bye")
    # while True:
    #     # print("running")
    #     trade_result = trade_results.get()
    #     yield trade_result
    #     time.sleep(2)


# print(live_trading("AAPL"))
# if __name__ == '__main__':
#     while True:
#         gen = run_processes("AAPL")
#         next(gen)