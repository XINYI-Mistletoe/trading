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
    v = len(get_time_sales("RY",tick))
    print(v)
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


while True:
    # for i in range(3):
    i = 1
    t = 1
    best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread(i,t), 'action': 'BUY'})
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread(i,t), 'action': 'SELL'})
 
    best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread(i,t), 'action': 'BUY'})
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread(i,t), 'action': 'SELL'})
   
    best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread(i,t), 'action': 'BUY'})
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread(i,t), 'action': 'SELL'})
 
    best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread(i,t), 'action': 'BUY'})
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread(i,t), 'action': 'SELL'})
    
    best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread(i,t), 'action': 'BUY'})
    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread(i,t), 'action': 'SELL'})
    sleep(0.25)
    while True:
        
        sleep(0.1)
        buy_orders,sell_orders = get_open_orders(ticker_list[i])
        if (buy_orders == []) and (sell_orders == []) and (net_position(i) == 0):
            print('clear up!')
            break
        elif (buy_orders == []) and (sell_orders != []) and (net_position(i) > 0):
            print('open sell')
            new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
            sell_limit_p = max([each['price'] for each in sell_orders])
            if (abs(new_ask_price - sell_limit_p) <= 0.02) and (t <= 15):
                t += 1
                continue
            else:
                while (get_open_orders(ticker_list[i]) != ([],[])):
                    resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                x = net_position(i)
                while abs(x) > 5000:
                    new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': new_ask_price+spread(i,t), 'action': 'SELL'})
                    x = abs(x)-5000
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': abs(x), 'price': new_ask_price-spread(i,t), 'action': 'SELL'})
                t += 1
        elif (buy_orders != []) and (sell_orders == []) and (net_position(i) < 0):
            print('open buy')
            new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
            buy_limit_p = min([each['price'] for each in buy_orders])
            if (abs(new_bid_price - buy_limit_p) <= 0.02) and (t <= 15):
                t += 1
                continue
            else:
                while (get_open_orders(ticker_list[i]) != ([],[])):
                    resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                x = net_position(i)
                while abs(x) > 5000:
                    new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': new_ask_price+spread(i,t), 'action': 'BUY'})
                    x = abs(x)-5000
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': abs(x), 'price': new_ask_price-spread(i,t), 'action': 'BUY'})
                t += 1
        else:
            if t <= 20:
                t += 1
                continue
            else:
                print('need to clear up')
                while (get_open_orders(ticker_list[i]) != ([],[])):
                    resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                while True:
                    sleep(0.05)
                    x = net_position(i)
                    if x < 0:
                        while abs(x) >= 5000:
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'BUY'})
                            sleep(0.05)
                            x = abs(x)-5000
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'BUY'})
                        print(resp.ok)
                    elif x > 0:
                        while abs(x) >= 5000:
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
                            sleep(0.05)
                            x = abs(x)-5000
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'SELL'})
                        print(resp.ok)
                    elif net_position(i) == 0:
                        break
                    else:
                        sleep(0.05)
            
    
