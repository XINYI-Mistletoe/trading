
import requests
from time import sleep
import signal
import sys
import os

s = requests.Session()
s.headers.update({'X-API-key': 'OFU9ARTN'})

# parameter setting
speedbump = 0.5
MAX_LONG_EXPOSURE = 25000
MAX_SHORT_EXPOSURE = -25000
ORDER_LIMIT = 5000
def get_open_orders(ticker): 
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/orders', params = payload)
    if resp.ok:
        orders = resp.json()
        buy_orders = [item for item in orders if item["action"] == "BUY"]
        sell_orders = [item for item in orders if item["action"] == "SELL"]
        return buy_orders, sell_orders
resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': "RY", 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': 4, 'action': 'BUY'})
esp = s.post('http://localhost:9999/v1/orders', params = {'ticker': "RY", 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': 4, 'action': 'BUY'})
buy_orders,sell_orders = get_open_orders("RY")
x = [{'order_id': 16974, 'period': 1, 'tick': 167, 'trader_id': '1009846981', 'ticker': 'RY', 'quantity': 5000.0, 'price': 4.0, 'type': 'LIMIT', 'action': 'BUY', 'quantity_filled': 0.0, 'vwap': None, 'status': 'OPEN'}, {'order_id': 16970, 'period': 1, 'tick': 167, 'trader_id': '1009846981', 'ticker': 'RY', 'quantity': 5000.0, 'price': 4.0, 'type': 'LIMIT', 'action': 'BUY', 'quantity_filled': 0.0, 'vwap': None, 'status': 'OPEN'}]
q = sum([each['quantity'] for each in x])
print(q)
# resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': 'RY'})