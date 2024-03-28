
import requests
from time import sleep
import signal
import sys
import os
import numpy as np



s = requests.Session()
s.headers.update({'X-API-key': 'OFU9ARTN'}) # Make sure you use YOUR API Key
# def get_tick():   
#     resp = s.get('http://localhost:9999/v1/case')
#     if resp.ok:
#         case = resp.json()
#         return case['tick'], case['status']
# def history_price_limit(ticker,limit = 60):
#     tick,status = get_tick()
#     resp = s.get('http://localhost:9999/v1/securities/history',params ={'ticker':ticker,'limit':limit})
#     print(resp.ok)
#     if resp.ok:
#         history = resp.json()
#         print(history)
#         highest = max([i['high'] for i in history])
#         lowest = min([i['low'] for i in history])
#         return highest,lowest
# highest,lowest= history_price_limit('UB',limit = 60)
# print(highest,lowest)
# def get_tick():   
#     resp = s.get('http://localhost:9999/v1/case')
#     if resp.ok:
#         case = resp.json()
#         return case['tick'], case['status']
# def history_price_limit(ticker,limit = 60):
#     tick,status = get_tick()
#     resp = s.get('http://localhost:9999/v1/securities/history',params ={'ticker':ticker,'limit':limit})
#     print(resp.ok)
#     if resp.ok:
#         history = resp.json()
#         highest = max([i['high'] for i in history])
#         lowest = min([i['low'] for i in history])
#         return highest,lowest
# history_data = np.array([0., 0., 0., 0., 0., 0.]).reshape(3,2)
# ticker_list = ['UB','GEM','ETF']
# for i, ticker_symbol in enumerate(ticker_list):
#     history_data[i, 1],history_data[i, 0] = history_price_limit(ticker_symbol,limit = 120)
#     print('history_data',history_data)

X = np.array([1., 2., 5., 6., 8., 9.]).reshape(3,2)
Y = np.array([0, 0, 0., 0., 0, 0.]).reshape(3,2)

for x,h in zip(X,Y):
    print(x[0])

