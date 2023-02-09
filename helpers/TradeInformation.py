try:
    from utils import getApi
except:
    from helpers.utils import getApi

api = getApi()

import csv


class TradeInformation:
    def __init__(self):
        self.symbol = ""
        self.trade_time = ""
        self.qty = ""
        self.price = ""
        self.realized_pnl = 0
        self.unrealized_pnl = 0
        self.return_percent = 0
        self.total_pnl = 0

    def update_trade(self, symbol, trade_time, qty, price):
        self.symbol = symbol
        self.trade_time = trade_time
        self.qty = qty
        self.price = price
        
    def update_metrics(self,symbol, trade_results):
        current_price = api.get_last_trade(symbol).price
        position = api.get_position(symbol)
        self.realized_pnl = 0
        for trade in trade_results:
            self.realized_pnl += (current_price - trade['price']) * trade['qty'] if trade['side'] == 'buy' else (trade['price'] - current_price) * trade['qty']

        self.unrealized_pnl = (current_price - position.avg_cost) * position.qty if position else 0
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        self.return_percent = self.total_pnl / (position.avg_cost * position.qty) if position else 0

        data =  {
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'total_pnl': self.total_pnl,
            'return_percent': self.return_percent
        }
        
        with open('../resources/data.csv', 'w+', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Realized_PNL', 'UnRealized_PNL', 'Total_PNL','return_percentage'])
            writer.writeheader()
            writer.writerows(data)
        return data
        
    def get_metrics(self):
        return {
            'symbol': self.symbol,
            'trade_time': self.trade_time,
            'qty': self.qty,
            'price': self.price,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl
        }

        
    def __str__(self):
        return f'Symbol: {self.symbol}\nTime: {self.time}\nShares: {self.shares}\nPrice: {self.price}'