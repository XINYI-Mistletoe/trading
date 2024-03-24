import requests
from time import sleep
import signal
import sys

class ApiException(Exception):
    pass

def signal_handler(signum,frame):
    global shutdown
    signal.signal(signal.SIGINT,signal.SGI_DFL)
    shutdown = True


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

def get_time_sales(ticker): 
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        time_sales_book = [item["quantity"] for item in book]
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
    return spread_dict[ticker_i]*10/t




ticker_list = ['CNR','RY']
spread_dict = [0.0027, 0.002,0.0015]

while True:
    for i in range(2): 
        i = 1
        best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread_dict[i], 'action': 'BUY'})
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread_dict[i], 'action': 'SELL'})
        sleep(0.1)
        best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread_dict[i], 'action': 'BUY'})
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread_dict[i], 'action': 'SELL'})
        sleep(0.1)
        best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread_dict[i], 'action': 'BUY'})
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread_dict[i], 'action': 'SELL'})
        sleep(0.1)
        best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread_dict[i], 'action': 'BUY'})
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread_dict[i], 'action': 'SELL'})
        sleep(0.1)
        best_bid_price, best_ask_price = get_bid_ask(ticker_list[i])
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price-spread_dict[i], 'action': 'BUY'})
        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price+spread_dict[i], 'action': 'SELL'})
        
        t = 1
        while True:
            sleep(0.2)
            buy_orders,sell_orders = get_open_orders(ticker_list[i])
            position = get_position()
            sleep(0.05)
            if (buy_orders == []) and (sell_orders == []) and (position == 0):
                print('clear')
                break
            elif buy_orders == [] and sell_orders != []:
                print('open sell')
                new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                if (best_ask_price - new_ask_price < 0.1) and (t <= 10):
                    print('pause')
                    t +=1
                    continue
                else:
                    buy_orders,sell_orders = get_open_orders(ticker_list[i])
                    if (buy_orders == []) and (sell_orders == []):
                        continue
                    else:
                        resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                        sleep(0.05)
                        x = net_position(i)
                        while abs(x) > 5000:
                            new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': 5000, 'price': new_ask_price+spread_dict[i], 'action': 'SELL'})
                            x = abs(x)-5000
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': abs(x), 'price': new_ask_price+spread_dict[i], 'action': 'SELL'})

            elif buy_orders != [] and sell_orders == []:
                print('open buy')
                new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                if (new_bid_price - best_bid_price < 0.1) and (t <= 10):
                    print('pause')
                    t += 1
                    continue
                else:
                    buy_orders,sell_orders = get_open_orders(ticker_list[i])
                    if (buy_orders == []) and (sell_orders == []):
                        continue
                    else:
                        resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                        sleep(0.05)
                        x = net_position(i)
                        while abs(x) > 5000:
                            new_bid_price, new_ask_price = get_bid_ask(ticker_list[i])
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': 5000, 'price': new_bid_price-spread_dict[i], 'action': 'BUY'})
                            x = abs(x)-5000
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': abs(x), 'price': new_bid_price-spread_dict[i], 'action': 'BUY'})

            else:
                print('both open')
                if t <= 15:
                    t +=1
                    continue
                else:
                    print('need to clear up')
                    resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker_list[i]})
                    sleep(0.05)
                    x = net_position(i)
                    sleep(0.1)
                    if x > 0:
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'SELL'})
                    else:
                        resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'BUY'})
                    sleep(0.05)
                    if resp.ok != True:
                        x = net_position(i)
                        sleep(0.1)
                        if x == 0:
                            continue
                        elif x > 0:
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'SELL'})
                        else:
                            resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(x), 'action': 'BUY'})
            t += 1



    
    
    
            


