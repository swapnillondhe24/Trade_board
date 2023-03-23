import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime

# Your credentials here

import alpaca_trade_api as tradeapi
from ..helpers.utils import write_order_to_csv,getKey,getSecret,write_to_log
from ..helpers.tradeinfo import start_trading


"""
You have 3 options:
 - backtest (IS_BACKTEST=True, IS_LIVE=False)
 - paper trade (IS_BACKTEST=False, IS_LIVE=False)
 - live trade (IS_BACKTEST=False, IS_LIVE=True)
"""



class SmaCross1(bt.Strategy):
    def notify_fund(self, cash, value, fundvalue, shares):
        super().notify_fund(cash, value, fundvalue, shares)

    def notify_store(self, msg, *args, **kwargs):
        super().notify_store(msg, *args, **kwargs)
        write_to_log(msg)

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

    # def log(self, txt, dt=None):
        # dt = dt or self.data.datetime[0]
        # dt = bt.num2date(dt)
        # print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        write_to_log("placing trade for {}. target size: {}".format(
            trade.getdataname(),
            trade.size),"crossover")

    def notify_order(self, order):
        write_to_log(order,"crossover")
        write_order_to_csv(order)
        print(f"Order notification. status{order.getstatusname()}.")
        print(f"Order info. status{order.info}.")

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



IS_BACKTEST = False
IS_LIVE = False
symbol = "TSLA"

import pandas as pd
import quantstats as qs
if __name__ == '__main__':

    # TODO add quantstats and test

    import logging
    logging.basicConfig(filename="./Trade_board/resources/crossover_logs.log",filemode='a+',format='%(asctime)s %(message)s', level=logging.WARNING)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross1)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=getKey(),
        secret_key=getSecret(),
        paper=not IS_LIVE,
    )

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    if True:
        data0 = DataFactory(dataname=symbol,
                            historical=True,
                            fromdate=datetime(2020, 7, 1),
                            todate=datetime(2021, 7, 11),
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


    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
    
    strats = cerebro.run()




    strat_return = strats[0].analyzers.getbyname("returns").get_analysis()
    print("*******************",strat_return)
    strat_return = list(strat_return.items())
    idx, values = zip(*strat_return)
    strat_return = pd.Series(values, idx)

    qs.reports.html(strat_return,output="crossover.html", title="Crossover Strategy")
    # start_trading(cerebro.run)
