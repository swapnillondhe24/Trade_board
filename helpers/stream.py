from alpaca_trade_api.common import URL
from alpaca_trade_api.stream import Stream
import os

async def trade_callback(t):
    print('trade', t)


async def quote_callback(q):
    print('quote', q)

from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv('API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('SECRET_ACCESS_KEY')
# Initiate Class Instance
stream = Stream(ALPACA_API_KEY,
                ALPACA_SECRET_KEY,
                base_url=URL('https://paper-api.alpaca.markets'),
                data_feed='iex')  # <- replace to 'sip' if you have PRO subscription

# subscribing to event
stream.subscribe_trades(trade_callback, 'AAPL')
stream.subscribe_quotes(quote_callback, 'IBM')
# while True:
stream.run()
print(stream)