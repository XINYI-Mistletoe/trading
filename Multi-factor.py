
import requests
from time import sleep
import signal
import sys
import os
import numpy as np
# import pandas as pd


s = requests.Session()
s.headers.update({'X-API-key': 'ABCDEFG'})

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
        buy_orders = [item for item in orders if item["action"] == "BUY" if item['ticker'] == ticker]
        sell_orders = [item for item in orders if item["action"] == "SELL" if item['ticker'] == ticker]
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

# def spread(ticker_i,t):
#     p = get_time_sales(ticker_list[ticker_i])
#     v =len(p)
#     if v > 25:
#         return spread_dict[ticker_i]/(t*t)
#     elif v > 12:
#         return 0.005/(t*t)
#     else:
#         return 0.01/(t*t)
def spread(ticker_i,t):
    v = len(get_time_sales(ticker_list[ticker_i]))
    if v > 25:
        return 0.01/(t*t)
    elif v > 12:
        return 0.005/(t*t)
    else:
        return spread_dict[ticker_i]/(t*t)
        
def get_time_sales(ticker): 
    tick,status = get_tick()
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        p = [item['quantity'] for item in book if item['tick'] == tick]
        return p

#parameters
MAX_LONG_EXPOSURE = 25000
MAX_SHORT_EXPOSURE = -25000
ORDER_LIMIT = [500,5000,200]
ticker_list = ['CNR','RY','AC']
spread_dict = [0.0027, 0.002,0.0015]
market_price = np.array([0., 0., 0., 0., 0., 0.]).reshape(3,2)


# os._exit(0)

while True:
    t = np.array([1,1,1])
    print('start')
    for i in range(2):
        if i == 0:
            for l in range(15):
                best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': best_bid_price-spread(i,t[i]), 'action': 'BUY'})
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': best_ask_price+spread(i,t[i]), 'action': 'SELL'})
               
        elif i == 1:
            for l in range(4):
                best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': best_bid_price-spread(i,t[i]), 'action': 'BUY'})
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': best_ask_price+spread(i,t[i]), 'action': 'SELL'})
                
        else:
            for l in range(15):
                best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': best_bid_price-spread(i,t[i]), 'action': 'BUY'})
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity':ORDER_LIMIT[i], 'price': best_ask_price+spread(i,t[i]), 'action': 'SELL'})
        sleep(0.25)
    while True:
        if get_position() == 0:
            print('all clear up!')
            break
        for i in range(2):
            sleep(0.1)
            buy_orders,sell_orders = get_open_orders(ticker_list[i])
            if (buy_orders == []) and (sell_orders == []) and (net_position(i) == 0):
                print('clear up!')
                continue
            elif (buy_orders == []) and (sell_orders != []) and (net_position(i) > 0):
                print(f'open sell {ticker_list[i]}')
                new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                sell_limit_p = max([each['price'] for each in sell_orders])
                if (abs(new_ask_price - sell_limit_p) <= 0.02) and (t[i] <= 3):
                    t[i] += 1
                    continue
                else:
                    while (get_open_orders(ticker_list[i]) != ([],[])):
                        resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                    x = net_position(i)
                    while abs(x) > ORDER_LIMIT[i]:
                        new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': new_ask_price+spread(i,t[i]), 'action': 'SELL'})
                        x = abs(x)-ORDER_LIMIT[i]
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': abs(x), 'price': new_ask_price-spread(i,t[i]), 'action': 'SELL'})
                    t[i] += 1
            elif (buy_orders != []) and (sell_orders == []) and (net_position(i) < 0):
                print(f'open buy {ticker_list[i]}')
                new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                buy_limit_p = min([each['price'] for each in buy_orders])
                if (abs(new_bid_price - buy_limit_p) <= 0.02) and (t[i] <= 3):
                    t[i] += 1
                    continue
                else:
                    while (get_open_orders(ticker_list[i]) != ([],[])):
                        resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                    x = net_position(i)
                    while abs(x) > ORDER_LIMIT[i]:
                        new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT[i], 'price': new_ask_price+spread(i,t[i]), 'action': 'BUY'})
                        x = abs(x)-ORDER_LIMIT[i]
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': abs(x), 'price': new_ask_price-spread(i,t[i]), 'action': 'BUY'})
                    t[i] += 1
            else:
                if t[i] <= 7:
                    t[i] += 1
                    continue
                else:
                    print('need to clear up',ticker_list[i])
                    while (get_open_orders(ticker_list[i]) != ([],[])):
                        resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                    while True:
                        print('market order',ORDER_LIMIT[i],ticker_list[i])
                        sleep(0.05)
                        x = net_position(i)
                        if x < 0:
                            while abs(x) >= ORDER_LIMIT[i]:
                                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': ORDER_LIMIT[i], 'action': 'BUY'})
                                sleep(0.05)
                                x = abs(x)-ORDER_LIMIT[i]
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'BUY'})
                            # print(resp.ok)
                        elif x > 0:
                            while abs(x) >= ORDER_LIMIT[i]:
                                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': ORDER_LIMIT[i], 'action': 'SELL'})
                                sleep(0.05)
                                x = abs(x)-ORDER_LIMIT[i]
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'SELL'})
                            # print(resp.ok)
                        elif x == 0:
                            break
                        else:
                            sleep(0.05)

