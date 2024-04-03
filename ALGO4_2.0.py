import requests
from time import sleep
import numpy as np

s = requests.Session()
s.headers.update({'X-API-key': 'ABCDEFG'}) # Make sure you use YOUR API Key

# global variables
MAX_LONG_EXPOSURE_NET = 25000
MAX_SHORT_EXPOSURE_NET = -25000
MAX_EXPOSURE_GROSS = 500000
ORDER_LIMIT = 25000

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
        gross_position = abs(book[1]['position']) + abs(book[2]['position']) + 2 * abs(book[3]['position'])
        net_position = book[1]['position'] + book[2]['position'] + 2 * book[3]['position']
        return gross_position, net_position

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


def main():
    print('ok')
    tick, status = get_tick()
    ticker_list = ['RGLD','RFIN','INDX']
    market_prices = np.array([0.,0.,0.,0.,0.,0.])
    market_prices = market_prices.reshape(3,2)
    resp = s.get('http://localhost:9999/v1/assets', params = {'ticker': 'ETF-Creation'})
    
    resp = s.post('http://localhost:9999/v1/leases', params = {'ticker': 'ETF-Creation'})  

    resp = s.post('http://localhost:9999/v1/leases', params = {'ticker': 'ETF-Redemption'})

    resp = s.get('http://localhost:9999/v1/leases')
    while not(resp.ok):
        resp = s.get('http://localhost:9999/v1/leases')
    leases = resp.json()
    creation_id = 'http://localhost:9999/v1/leases/' + str(leases[0]['id'])
    redemption_id = 'http://localhost:9999/v1/leases/' + str(leases[1]['id'])
    currency = 2*ORDER_LIMIT * 0.0375
    volume = 2*ORDER_LIMIT
    
    while True:         
        for i, ticker_symbol in enumerate(ticker_list):
            market_prices[i, 0], market_prices[i, 1] = get_bid_ask(ticker_symbol)
        if market_prices[0, 0] + market_prices[1, 0] > market_prices[2, 1] + 0.06251: # 0.0375 + 0.025
            
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX', 'type': 'MARKET', 'quantity': ORDER_LIMIT,  'action': 'BUY'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX', 'type': 'MARKET', 'quantity': ORDER_LIMIT,  'action': 'BUY'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
            while True:
                resp = s.post(redemption_id, params = {'from1': 'INDX', 'quantity1': volume, 'from2': 'CAD', 'quantity2': currency})
                if resp.ok == True:
                    break

        elif market_prices[0, 1] + market_prices[1, 1] + 0.0251 < market_prices[2, 0]:    
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'BUY'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'BUY'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'BUY'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'SELL'})
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN', 'type': 'MARKET', 'quantity': ORDER_LIMIT, 'action': 'BUY'})
            while True:
                resp = s.post(creation_id, params = {'from1': 'RGLD', 'quantity1': 2*ORDER_LIMIT, 'from2': 'RFIN', 'quantity2': 2*ORDER_LIMIT})
                if resp.ok == True:
                    break
        sleep(0.01)
        # tick, status = get_tick()

if __name__ == '__main__':
    main()



