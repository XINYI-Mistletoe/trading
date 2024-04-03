import requests
from time import sleep
import numpy as np

s = requests.Session()
s.headers.update({'X-API-key': 'ABCDEFG'}) # Make sure you use YOUR API Key

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
def get_tick():   
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']

def get_news(estimates_data,news_query_length): 
    resp = s.get ('http://localhost:9999/v1/news')
    if resp.ok:
        news_query = resp.json()
        news_query_length_check = len(news_query)
        
        if news_query_length_check > news_query_length:
            news_query_length = news_query_length_check
            
            newest_tick = news_query[0]['tick']
            start_char = news_query[0]['body'].find("$")
            newest_estimate = float(news_query[0]['body'][start_char + 1 : start_char + 6])
                        
            if news_query[0]['headline'].find("UB") > 0:
                estimates_data[0,0] = max(newest_estimate - ((300 - newest_tick) / 50), estimates_data[0,0])
                estimates_data[0,1] = min(newest_estimate + ((300 - newest_tick) / 50), estimates_data[0,1])
           
            elif news_query[0]['headline'].find("GEM") > 0:
                estimates_data[1,0] = max(newest_estimate - ((300 - newest_tick) / 50), estimates_data[1,0])
                estimates_data[1,1] = min(newest_estimate + ((300 - newest_tick) / 50), estimates_data[1,1])
            
        estimates_data[2,0] = estimates_data[0,0] + estimates_data[1,0]
        estimates_data[2,1] = estimates_data[0,1] + estimates_data[1,1]
                
        return estimates_data, news_query_length 
def get_position():
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        gross_position = abs(book[0]['position']) + abs(book[1]['position']) + 2 * abs(book[2]['position'])
        # net_position = book[0]['position'] + book[1]['position'] + 2 * book[2]['position']
        return gross_position
def get_open_orders(ticker): 
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/orders', params = payload)
    if resp.ok:
        orders = resp.json()
        buy_orders = [item for item in orders if (item["action"] == "BUY")]
        sell_orders = [item for item in orders if (item["action"] == "SELL")]
        return buy_orders, sell_orders
def get_mini_open_orders(ticker,quantity): 
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/orders', params = payload)
    if resp.ok:
        orders = resp.json()
        buy_orders = [item for item in orders if (item["action"] == "BUY" and item["quantity"] == quantity)]
        sell_orders = [item for item in orders if (item["action"] == "SELL"and item["quantity"] == quantity)]
        return buy_orders, sell_orders

def net_max_position():
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        max_num = [abs(s["position"]) for s in book]
        max_index = max_num.index(max(max_num))
        return max_index,max_num
def history_price_limit(ticker,limit = 60):
    tick,status = get_tick()
    resp = s.get('http://localhost:9999/v1/securities/history',params ={'ticker':ticker,'limit':limit})
    # print(resp.ok)
    if resp.ok:
        history = resp.json()
        highest = max([i['high'] for i in history])
        lowest = min([i['low'] for i in history])
        return highest,lowest

def net_position(i):
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        return book[i]['position']
# Parameter
ORDER_LIMIT = 5000
ORDER_MARKET = 500
ticker_list = ['UB','GEM','ETF']
# Market price
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
# currency = ORDER_MARKET* 0.0375
# volume = ORDER_MARKET
#
news_query_length = 1
estimates_data = np.array([40., 60., 20., 30., 60., 90]).reshape(3,2)
old_estimates_data = np.array([40., 60., 20., 30., 60., 90.]).reshape(3,2)
history_data = np.array([0., 0., 0., 0., 0., 0.]).reshape(3,2)

while True:
    # update new estimate prices
    print('start')
    gross_position = get_position()
    # main
    estimates_data, news_query_length = get_news(estimates_data, news_query_length) 
    if not(np.array_equal(estimates_data,old_estimates_data)):
        print('limit change')
        if 7 <=news_query_length :
            for i, ticker_symbol in enumerate(ticker_list):
                history_data[i, 1],history_data[i, 0] = history_price_limit(ticker_symbol,limit = 120)
        for x,y,h,ticker in zip(estimates_data,old_estimates_data,history_data,ticker_list):
            if x[0] > x[1]:
                print('error')
                sleep(10)
                continue
            elif x[0]<h[1]< x[1]:
                ask_price = min(x[1],y[1],h[1])+0.02
            elif x[1] > h[0] > x[0]:
                bid_price = max(x[0],y[0],h[0])-0.02
            else:
                ask_price = min(x[1],y[1]) + 0.02
                bid_price = max(x[0],y[0]) - 0.02
            # sleep(0.1)
            
            resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker})
            while resp.ok != True:
                print('cancel')
                resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': ticker})
            for p in range(7):
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker, 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': bid_price, 'action': 'BUY'})
                sleep(0.05)
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker, 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': ask_price, 'action': 'SELL'})

           
    old_estimates_data = estimates_data.copy()
    print("range",estimates_data,news_query_length)
    position_num = 100
    # update market prices
    for i, ticker_symbol in enumerate(ticker_list):
        market_prices[i, 0], market_prices[i, 1] = get_bid_ask(ticker_symbol)
    if market_prices[0, 0] + market_prices[1, 0] > market_prices[2, 1] + 0.0975:
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'UB', 'type': 'MARKET', 'quantity': position_num, 'action': 'SELL'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'ETF', 'type': 'MARKET', 'quantity': position_num,  'action': 'BUY'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'GEM', 'type': 'MARKET', 'quantity': position_num, 'action': 'SELL'})
        while True:
            print('*')
            resp = s.post(redemption_id, params = {'from1': 'ETF', 'quantity1': position_num, 'from2': 'CAD', 'quantity2': position_num* 0.0375})
            if resp.ok == True:
                break
        print('arbitrage')
    elif market_prices[0, 1] + market_prices[1, 1] + 0.06 < market_prices[2, 0]: 
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'UB', 'type': 'MARKET', 'quantity': position_num, 'action': 'BUY'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'ETF', 'type': 'MARKET', 'quantity': position_num, 'action': 'SELL'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'GEM', 'type': 'MARKET', 'quantity': position_num, 'action': 'BUY'})
        while True:
            print('*')
            resp = s.post(creation_id, params = {'from1': 'UB', 'quantity1': position_num, 'from2': 'GEM', 'quantity2': position_num})
            if resp.ok == True:
                break
        print('arbitrage')
    else:
        # continue
        # position_num = 100
        # spread = market_prices[:,1] - market_prices[:,0]
        # if max(spread) >= 0.7:
        #     print('limit order')
        #     i = np.argmax(spread)
        #     ticker = ticker_list[i]
        #     best_bid_price = market_prices[i,0]+0.2
        #     best_ask_price = market_prices[i,1]-0.2
        #     resp_buy = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': position_num, 'price': best_bid_price, 'action': 'BUY'})
        #     resp_sell = s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'LIMIT', 'quantity': position_num, 'price': best_ask_price, 'action': 'SELL'})
        #     if resp_buy.ok and resp_sell.ok:
        #         buy_id = resp_buy.json()["order_id"]
        #         sell_id = resp_sell.json()["order_id"]
        #     else:
        #         continue
        #     sleep(0.3)
        #     while True:
        #         # sleep(0.1)
        #         buy_orders,sell_orders = get_mini_open_orders(ticker_list[i],position_num)
        #         if get_mini_open_orders(ticker_list[i],position_num) == ([],[]):
        #             print('clear')
        #             break
        #         elif buy_orders == [] and sell_orders != []:
        #             print('open sell')
        #             unfilled_q = sell_orders[0]["quantity"] - sell_orders[0]["quantity_filled"]
        #             while (get_mini_open_orders(ticker_list[i],position_num) != ([],[])):
        #                 resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ids': sell_id})
        #                 # sleep(0.2)
        #             resp= s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': unfilled_q,'action': 'SELL'})
        #         elif buy_orders != [] and sell_orders == []:
        #             print('open buy')
        #             unfilled_q = buy_orders[0]["quantity"] - buy_orders[0]["quantity_filled"]
        #             while (get_mini_open_orders(ticker_list[i],position_num) != ([],[])):
        #                 resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ids':buy_id})
        #             resp= s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': unfilled_q, 'action': 'BUY'})
        #         else:
        #             print('both')
        #             try:
        #                 net = buy_orders[0]["quantity_filled"] - sell_orders[0]["quantity_filled"]
        #                 while (get_mini_open_orders(ticker_list[i],position_num) != ([],[])):
        #                     print('cancel failed')
        #                     resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ids':sell_id})
        #                     resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ids': buy_id})
        #                 if net > 0:
        #                     resp= s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(net),  'action': 'SELL'})
        #                 else:
        #                     resp= s.post('http://localhost:9999/v1/orders', params = {'ticker': ticker_list[i], 'type': 'MARKET', 'quantity': abs(net),  'action': 'BUY'})
        #             except:
        #                 continue
                


# if __name__ == '__main__':
#     main()