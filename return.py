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

resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RY', 'type': 'LIMIT', 'quantity': 1000, 'price':0.0001,action': 'SELL'})
print(resp.ok)
# resp = s.get ('http://localhost:9999/v1/securities')
# if resp.ok:
#     book = resp.json()
#     print(book[1],"\n")
