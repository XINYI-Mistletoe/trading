import requests
import yaml
with open ('env.yaml','r') as f:
    ENV = yaml.safe_load(f)

import requests
def main():
    with requests.Session() as s:
        s.headers.update(ENV['API_KEY'])
        lmt_sell_params = {'ticker': 'CRZY', 'type': 'LIMIT', 'quantity': 2000,'price': 10.00, 'action': 'SELL'}
        resp = s.post('http://localhost:9999/v1/orders', params=lmt_sell_params)
        if resp.ok:
            lmt_order = resp.json()
            id = lmt_order['order_id']
            print('The limit sell order was submitted and has ID', id)
        else:
            print('The order was not successfully submitted!')
if __name__ == '__main__':
    main()