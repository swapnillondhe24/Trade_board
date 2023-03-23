import alpaca_backtrader_api
import backtrader as bt
import pandas as pd
import numpy as np
from ..helpers.utils import write_order_to_csv, getKey,getSecret,write_to_log
from ..helpers.tradeinfo import start_trading
from datetime import datetime


class PairsTradingStrategy(bt.Strategy):
    
    params = dict(
        lookback=20,
        zscore_high=2.0,
        zscore_low=-2.0,
        half_spread=0.01,
        qty1=1000,
        qty2=1000,
        status='out'
    )
    
    def __init__(self):
        self.data1 = self.datas[0]
        self.data2 = self.datas[1]
        
        self.spread = self.data1 - self.data2
        self.spread_ma = bt.indicators.SimpleMovingAverage(self.spread, period=self.params.lookback)
        self.spread_std = bt.indicators.StandardDeviation(self.spread, period=self.params.lookback)
        
    def next(self):
        zscore = (self.spread[0] - self.spread_ma[0]) / self.spread_std[0]
        
        if self.params.status == 'out':
            if zscore > self.params.zscore_high:
                self.params.status = 'short'
                self.sell(data=self.data1, size=self.params.qty1)
                self.buy(data=self.data2, size=self.params.qty2)
            elif zscore < self.params.zscore_low:
                self.params.status = 'long'
                self.buy(data=self.data1, size=self.params.qty1)
                self.sell(data=self.data2, size=self.params.qty2)
                
        elif self.params.status == 'short' and zscore < 0.0:
            self.params.status = 'out'
            self.buy(data=self.data1, size=self.params.qty1)
            self.sell(data=self.data2, size=self.params.qty2)
            
        elif self.params.status == 'long' and zscore > 0.0:
            self.params.status = 'out'
            self.sell(data=self.data1, size=self.params.qty1)
            self.buy(data=self.data2, size=self.params.qty2)


IS_BACKTEST = False
IS_LIVE = False
symbol1 = "GOOG"
symbol2 = "TSLA"

import quantstats as qs
import yfinance as yf

if __name__ =="__main__":
    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(PairsTradingStrategy)
    cerebro.broker.setcommission(commission=0.001)
    
    datapath = 'FB.csv'
    
    symbol = "GOOGL"
    symbol2 = "TSLA"
    
    
    API_KEY_ID = "PKNABMS522NZ2ETAGRVA"
    SECRET_ACCESS_KEY = "CigQCqpN5o8AyqfR97kbdw1RWJRowIZkM4O3QvXn"
    
    
    store = alpaca_backtrader_api.AlpacaStore(
            key_id=API_KEY_ID,
            secret_key=SECRET_ACCESS_KEY,
            paper=True,)
    
    
    DataFactory = store.getdata
    
    data = DataFactory(dataname=symbol,
                                historical=False,
                                timeframe=bt.TimeFrame.Ticks,
                                backfill_start=False,
                                data_feed='iex'
                                )
    
    data0 = DataFactory(dataname=symbol2,
                                historical=False,
                                timeframe=bt.TimeFrame.Ticks,
                                backfill_start=False,
                                data_feed='iex'
                                )
    
    cerebro.adddata(data)
    cerebro.adddata(data0)
    
    
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="return")
    
    results = cerebro.run()
    strat = results[0]
    
    
    strat_return = strat.analyzers.getbyname("return").get_analysis()
    strat_return = list(strat_return.items())
    idx, values = zip(*strat_return)
    strat_return = pd.Series(values, idx)
    
    qs.reports.html(strat_return,output="pairs.html")




exit(0)
if __name__ == '__main__':

    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(PairsTradingStrategy)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=getKey(),
        secret_key=getSecret(),
        paper=not IS_LIVE,
    )

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    if IS_BACKTEST:
        data1 = DataFactory(dataname=symbol1,
                            historical=True,
                            fromdate=datetime(2022, 7, 1),
                            todate=datetime(2022, 7, 11),
                            timeframe=bt.TimeFrame.Days,
                            data_feed='iex')
        data2 = DataFactory(dataname=symbol2,
                            historical=True,
                            fromdate=datetime(2022, 7, 1),
                            todate=datetime(2022, 7, 11),
                            timeframe=bt.TimeFrame.Days,
                            data_feed='iex')
    else:
        data1 = DataFactory(dataname=symbol1,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False,
                            data_feed='iex'
                            )
        data2 = DataFactory(dataname=symbol2,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False,
                            data_feed='iex'
                            )
        # or just alpaca_backtrader_api.AlpacaBroker()
        broker = store.getbroker()
        cerebro.setbroker(broker)
    
    cerebro.adddata(data1)
    cerebro.adddata(data2)

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    
    

    if input("Dashboard ? : ")=='y':
        start_trading(cerebro.run)
    else:
        cerebro.run()
    # cerebro.run()



