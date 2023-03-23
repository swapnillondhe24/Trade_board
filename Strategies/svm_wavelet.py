import backtrader as bt
import pandas as pd
from sklearn.svm import SVR
import pywt
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
import alpaca_backtrader_api
from datetime import datetime



from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os

from ..helpers.utils import write_order_to_csv, getKey,getSecret,write_to_log
from ..helpers.tradeinfo import start_trading


IS_BACKTEST = False
IS_LIVE = False
symbol = "GOOG"






class SVMWaveletStrategy(bt.Strategy):
    params = (('period', 10),
              ('num_periods', 3),
              ('svm_kernel', 'rbf'),
              ('svm_c', 1.0),
              ('svm_epsilon', 0.1))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.svm_model = None
        self.wavelet_coeffs = None
        self.predicted_values = []
        self.predicted_index = 0

    def next(self):
        if len(self) % self.params.period == 0:
            self.wavelet_coeffs = pywt.wavedec(self.dataclose.get(ago=0, size=self.params.period), 'db1', level=self.params.num_periods)

            input_features = []
            for coeff in self.wavelet_coeffs:
                input_features += coeff.tolist()

            if self.svm_model is None:
                self.svm_model = SVR(kernel=self.params.svm_kernel, C=self.params.svm_c, epsilon=self.params.svm_epsilon)
                X = pd.DataFrame(input_features).transpose()
                y = self.dataclose.get(ago=0, size=self.params.period).tolist()
                self.svm_model.fit(X, y)
            else:
                input_features.append(self.predicted_values[-1])
                X = pd.DataFrame(input_features).transpose()
                predicted_value = self.svm_model.predict(X)
                self.predicted_values.append(predicted_value[0])
                self.predicted_index = len(self.predicted_values) - 1

    def buy_signal(self):
        if self.predicted_index == len(self.predicted_values) - 1:
            return self.dataclose[0] < self.predicted_values[-1] and self.dataclose[1] > self.predicted_values[-2]
        return False

    def sell_signal(self):
        if self.predicted_index == len(self.predicted_values) - 1:
            return self.dataclose[0] > self.predicted_values[-1] and self.dataclose[1] < self.predicted_values[-2]
        return False
    
    def notify_trade(self, trade):
        write_to_log("placing trade for {}. target size: {}".format(
            trade.getdataname(),
            trade.size),"SVM")
        
    def notify_order(self, order):
        write_to_log(order,"SVM")
        write_order_to_csv(order)
        print(f"Order notification. status{order.getstatusname()}.")
        print(f"Order info. status{order.info}.")

class SVMWaveletBacktest(bt.Strategy):
    def __init__(self):
        self.strategy = SVMWaveletStrategy(self.params.period, self.params.num_periods, self.params.svm_kernel, self.params.svm_c, self.params.svm_epsilon)

    def next(self):
        if self.strategy.buy_signal():
            self.buy()
        elif self.strategy.sell_signal():
            self.sell()


IS_BACKTEST = False
IS_LIVE = False
symbol = "GOOG"



if __name__ == '__main__':

    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(SVMWaveletStrategy)

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
    