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

from datetime import datetime

import alpaca_backtrader_api
import backtrader as bt



IS_BACKTEST = False
IS_LIVE = False
symbol = 'AAPL'


class SmaCross1(bt.Strategy):
    def notify_fund(self, cash, value, fundvalue, shares):
        super().notify_fund(cash, value, fundvalue, shares)

    def notify_store(self, msg, *args, **kwargs):
        super().notify_store(msg, *args, **kwargs)
        self.log(msg)

    def notify_data(self, data, status, *args, **kwargs):
        super().notify_data(data, status, *args, **kwargs)
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        if data._getstatusname(status) == "LIVE":
            self.live_bars = True

    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        self.log("placing trade for {}. target size: {}".format(
            trade.getdataname(),
            trade.size))

    def notify_order(self, order):
        print(order)
        print(f"Order notification. status {order.getstatusname()}.")

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')

    def __init__(self):
        self.live_bars = False
        sma1 = bt.ind.SMA(self.data0, period=self.p.pfast)
        sma2 = bt.ind.SMA(self.data0, period=self.p.pslow)
        self.crossover0 = bt.ind.CrossOver(sma1, sma2)

    def next(self):
        #self.buy(data=data0, size=2)
        if not self.live_bars and not IS_BACKTEST:
            # only run code if we have live bars (today's bars).
            # ignore if we are backtesting
            return
        # if fast crosses slow to the upside
        if not self.positionsbyname[symbol].size and self.crossover0 > 0:
            self.buy(data=data0, size=5)  # enter long

        # in the market & cross to the downside
        if self.positionsbyname[symbol].size and self.crossover0 <= 0:
            self.close(data=data0)  # close long position


if __name__ == '__main__':
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross1)
    
    
    load_dotenv()

    API_KEY_ID = os.getenv('API_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
    
    store = alpaca_backtrader_api.AlpacaStore(
        key_id=API_KEY_ID,
        secret_key=SECRET_ACCESS_KEY,
        paper=not IS_LIVE,
    )

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    if IS_BACKTEST:
        data0 = DataFactory(dataname=symbol,
                            historical=True,
                            fromdate=datetime(2021, 7, 1),
                            todate=datetime(2022, 7, 11),
                            timeframe=bt.TimeFrame.Days,
                            data_feed='iex')
    else:
        data0 = DataFactory(dataname=symbol,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False,
                            data_feed='iex'
                            )
        # or just alpaca_backtrader_api.AlpacaBroker()
        broker = store.getbroker()
        cerebro.setbroker(broker)
    cerebro.adddata(data0)

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.run()
    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.plot()
    
    start_trading(symbol, signals ,'crossover_strategy',50)



if __name__=="__main__":
    crossover_strategy()