import backtrader as bt
import alpaca_backtrader_api
from ..helpers.utils import write_order_to_csv, getKey,getSecret,write_to_log
from ..helpers.tradeinfo import start_trading
from datetime import datetime

class WTI_Brent_Strategy(bt.Strategy):

    params = dict(
        wti_brent_spread=0.0,  # initial spread value
        wti_multiplier=1,      # WTI contract multiplier
        brent_multiplier=1,    # Brent contract multiplier
        wti_symbol='CL',       # WTI contract symbol
        brent_symbol='B',      # Brent contract symbol
        stake=1,               # number of contracts to trade
        printout=True          # print out trade details
    )

    def __init__(self):
        self.data_wti = self.getdatabyname(self.params.wti_symbol)
        self.data_brent = self.getdatabyname(self.params.brent_symbol)
        self.spread = bt.indicators.SimpleMovingAverage(
            self.data_wti - self.data_brent, period=30
        )
        self.signal = self.spread - self.params.wti_brent_spread

    def next(self):
        if self.position:
            if self.signal < 0:
                if self.params.printout:
                    print('SELL CREATE {} WTI {} BRENT {}'.format(
                        self.params.stake, self.data_wti.close[0], self.data_brent.close[0])
                    )
                self.sell(self.data_wti, size=self.params.stake*self.params.wti_multiplier)
                self.buy(self.data_brent, size=self.params.stake*self.params.brent_multiplier)
            elif self.signal > 0:
                if self.params.printout:
                    print('BUY CREATE {} WTI {} BRENT {}'.format(
                        self.params.stake, self.data_wti.close[0], self.data_brent.close[0])
                    )
                self.buy(self.data_wti, size=self.params.stake*self.params.wti_multiplier)
                self.sell(self.data_brent, size=self.params.stake*self.params.brent_multiplier)
        else:
            if self.signal > 0:
                if self.params.printout:
                    print('BUY CREATE {} WTI {} BRENT {}'.format(
                        self.params.stake, self.data_wti.close[0], self.data_brent.close[0])
                    )
                self.buy(self.data_wti, size=self.params.stake*self.params.wti_multiplier)
                self.sell(self.data_brent, size=self.params.stake*self.params.brent_multiplier)
            elif self.signal < 0:
                if self.params.printout:
                    print('SELL CREATE {} WTI {} BRENT {}'.format(
                        self.params.stake, self.data_wti.close[0], self.data_brent.close[0])
                    )
                self.sell(self.data_wti, size=self.params.stake*self.params.wti_multiplier)
                self.buy(self.data_brent, size=self.params.stake*self.params.brent_multiplier)


IS_BACKTEST = False
IS_LIVE = False
symbol = "GOOG"





if __name__ == '__main__':

    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(WTI_Brent_Strategy)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=getKey(),
        secret_key=getSecret(),
        paper=not IS_LIVE,
    )

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    if IS_BACKTEST:
        data0 = DataFactory(dataname=symbol,
                            historical=True,
                            fromdate=datetime(2020, 7, 1),
                            todate=datetime(2020, 7, 11),
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
    
    
    start_trading(cerebro.run)
    # cerebro.run()
    