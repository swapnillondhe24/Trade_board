import backtrader as bt
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
import alpaca_backtrader_api
from datetime import datetime

# TODO add quantstats and test

from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os

from ..helpers.utils import write_order_to_csv
from ..helpers.tradeinfo import start_trading

load_dotenv()

ALPACA_API_KEY = os.getenv('API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv("SECRET_ACCESS_KEY")
IS_BACKTEST = False
IS_LIVE = False
symbol = "GOOG"
def write_to_log(msg):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("./Trade_board/resources/GBMlogfile.txt", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")





class GBMStrategy(bt.Strategy):
    
    params = (
        ('n_estimators', 100),
        ('max_depth', 3),
        ('learning_rate', 0.1),
        ('random_state', 42),
    )
    
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=self.params.n_estimators,
            max_depth=self.params.max_depth,
            learning_rate=self.params.learning_rate,
            random_state=self.params.random_state
        )

    def notify_trade(self, trade):
        write_to_log("placing trade for {}. target size: {}".format(
            trade.getdataname(),
            trade.size))

    def notify_order(self, order):
        write_to_log(order)
        write_order_to_csv(order)

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')
        
    def next(self):
        # Get the current price data
        prices = self.datas[0]
        current_price = prices.close[0]
        
        # Get the previous price data
        previous_prices = prices.close.array[:-1]
        
        # Compute the price differences
        price_diffs = previous_prices - current_price
        
        # Compute the features
        features = pd.DataFrame({'price_diffs': price_diffs}).fillna(0)
        
        # Compute the predictions
        predictions = self.model.predict(features)
        
        # Buy if the model predicts an increase in price
        if predictions[-1] == 1:
            self.buy()
            
        # Sell if the model predicts a decrease in price
        elif predictions[-1] == -1:
            self.sell()



if __name__ == '__main__':

    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(GBMStrategy)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
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

    # cerebro.addanalyzer(BacktraderPlottingLive, address="*", port=8889)

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    
    
    if input("Want to start dasboard y/n ") == 'y':
        start_trading(cerebro.run)
    
    else:
        cerebro.run()
        # plot = btplotting.BacktraderPlotting()
        # cerebro.plot(plot, iplot=True)