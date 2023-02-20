import pandas as pd
import numpy as np
# from helpers.utils import getApi
from ..helpers.tradeinfo import live_trading


api = getApi()

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

    live_trading(symbol, signals ,50)