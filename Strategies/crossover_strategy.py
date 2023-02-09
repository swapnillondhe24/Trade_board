import pandas as pd
import numpy as np

class crossover_strategy:
    def crossover_strategy(data):
        short_window = 50
        long_window = 100
    
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0
    
        signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()
    
        signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] 
                                                > signals['long_mavg'][short_window:], 1.0, 0.0)   
        signals['positions'] = signals['signal'].diff()
    
        signals['signal'] = np.where(signals['signal'] == 0, 0.0, signals['signal'])
        signals['signal'] = np.where(signals['signal'] == 1, 1.0, signals['signal'])
        signals['signal'] = np.where(signals['positions'] == 0, 0.5, signals['signal'])
    
        return signals