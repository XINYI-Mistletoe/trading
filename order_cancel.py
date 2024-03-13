import requests
import yaml
with open ('env.yaml','r') as f:
    ENV = yaml.safe_load(f)

import requests
def main():
    with requests.Session() as s:
        s.headers.update(ENV['API_KEY'])
        order_id = 100 # assuming the order to cancel has ID 100
        resp = s.delete('http://localhost:9999/v1/orders/{}'.format(order_id))
        if resp.ok:
            status = resp.json()
            success = status['success']
            print('The order was successfully cancelled?', success)
if __name__ == '__main__':
    main()