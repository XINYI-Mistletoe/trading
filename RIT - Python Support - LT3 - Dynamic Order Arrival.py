import requests
from time import sleep
import signal
import sys
import os
import numpy as np
import pandas as pd

s = requests.Session()
s.headers.update({'X-API-key': 'ABCDEFG'})

# parameter setting
speedbump = 0.5
MAX_LONG_EXPOSURE = 25000
MAX_SHORT_EXPOSURE = -25000
ORDER_LIMIT = 5000

def get_tick():
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']

def get_bid_ask(ticker):
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/securities/book', params = payload)
    if resp.ok:
        book = resp.json()
        bid_side_book = book['bids']
        ask_side_book = book['asks']
        
        bid_prices_book = [item["price"] for item in bid_side_book]
        ask_prices_book = [item['price'] for item in ask_side_book]
        
        best_bid_price = bid_prices_book[0]
        best_ask_price = ask_prices_book[0]
  
        return best_bid_price, best_ask_price

def get_time_sales(ticker,tick): 
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        time_sales_book = [item["quantity"] for item in book if item["tick"] ==tick]
        return time_sales_book

def get_position():
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        return abs(book[0]['position']) + abs(book[1]['position']) + abs(book[2]['position']) 

def get_open_orders(ticker): 
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/orders', params = payload)
    if resp.ok:
        orders = resp.json()
        buy_orders = [item for item in orders if item["action"] == "BUY"]
        sell_orders = [item for item in orders if item["action"] == "SELL"]
        return buy_orders, sell_orders

def get_order_status(order_id): 
    resp = s.get ('http://localhost:9999/v1/orders' + '/' + str(order_id))
    if resp.ok:
        order = resp.json()
        return order['status']

def net_position(i):
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        return book[i]['position']

def spread(ticker_i,t):
    tick, status = get_tick()
    v = sum(get_time_sales("RY",tick))
    # print(tick,v)
    if v > 25:
        return 0.01/(t*t)
    elif v > 12:
        return 0.005/(t*t)
    else:
        return spread_dict[ticker_i]/(t*t)
    # return -0.001
# os._exit(0)

ticker_list = ['CNR','RY','AC']
spread_dict = [0.0027, 0.002,0.0015]
market_price = np.array([0., 0., 0., 0., 0., 0.]).reshape(3,2)


payload = {'ticker': 'AC'}
tick_list = list(range(1,250))
quantity_list = []
spread_list = []
resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
if resp.ok:
    book = resp.json()
    for t in tick_list:
        quantity = sum([item["quantity"] for item in book if item["tick"] ==t])
        spreadd = max([item["price"] for item in book if item["tick"] ==t]) - min([item["price"] for item in book if item["tick"] ==t])
        quantity_list.append(quantity)
        spread_list.append(spreadd)
df = pd.DataFrame({'tick':tick_list,'volume':quantity_list,'spread':spread_list})
df.to_excel('trade_info_ac.xlsx',index=False)

payload = {'ticker': 'CNR'}
tick_list = list(range(1,250))
quantity_list = []
spread_list = []
resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
if resp.ok:
    book = resp.json()
    for t in tick_list:
        quantity = sum([item["quantity"] for item in book if item["tick"] ==t])
        spreadd = max([item["price"] for item in book if item["tick"] ==t]) - min([item["price"] for item in book if item["tick"] ==t])
        quantity_list.append(quantity)
        spread_list.append(spreadd)
df = pd.DataFrame({'tick':tick_list,'volume':quantity_list,'spread':spread_list})
df.to_excel('trade_info_CNR.xlsx',index=False)

payload = {'ticker': 'RY'}
tick_list = list(range(1,250))
quantity_list = []
spread_list = []
resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
if resp.ok:
    book = resp.json()
    for t in tick_list:
        quantity = sum([item["quantity"] for item in book if item["tick"] ==t])
        spreadd = max([item["price"] for item in book if item["tick"] ==t]) - min([item["price"] for item in book if item["tick"] ==t])
        quantity_list.append(quantity)
        spread_list.append(spreadd)
df = pd.DataFrame({'tick':tick_list,'volume':quantity_list,'spread':spread_list})
df.to_excel('trade_info_ry.xlsx',index=False)
    

            