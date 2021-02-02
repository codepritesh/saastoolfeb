#coding:utf-8
import requests
import secrets


class moonix():

    def __init__(self, api_key, secret, base_url='https://api.moonix.io'):
        self.base_url = base_url
        self.api_key = api_key
        self.secret = secret

    def public_request(self, method, base_path, payload=None):
        """request public url"""
        full_url = self.base_url + base_path
        try:
            if method == "GET":
                r = requests.request(method, full_url, params=payload)
            else:
                r = requests.request(method, full_url, json=payload)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code}
        except requests.exceptions.ConnectionError as err:
            return False, {'error': 'E10001', 'data': err}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err}

    def signed_request(self, method, base_path, payload=None):
        """request a signed url"""
        full_url = self.base_url + base_path
        headers = {
                'X-Moonix-ApiKey': self.api_key,
                'X-Moonix-SecretKey': self.secret,
                }

        try:
            if method == "GET":
                r = requests.request(method, full_url, headers=headers, params=payload)
            else:
                r = requests.request(method, full_url, headers=headers, json=payload)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code, 'text': r.text}
        except requests.exceptions.HTTPError as err:
            return False, {'error': 'E10001', 'data': err, 'text': r.text}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err, 'text': r.text}

    def fetch_markets(self):
        return self.public_request('POST', f'/api/markets')

    def fetch_balance(self, coin):
        params = [{"coin":coin.upper()}]
        return self.signed_request('POST', f'/api/balance', payload=params)

    def create_order(self, symbol, type, side, quantity, price, dummy_params={}):
        params = [{"coinpair":symbol},{"amount":str(quantity)}, {"price":str(price)}, {"hash": secrets.token_hex(32)}]
        if side == 'buy':
            order = self.signed_request('POST', f'/api/buy', payload=params)
        elif side == 'sell':
            order = self.signed_request('POST', f'/api/sell', payload=params)
        print('Order is {}__{}'.format(order, order[-1].get('OrderId')))
        # (True, {'OrderId': '', 'From_Wallet_Balance': '', 'To_Wallet_Balance': '', 'Status': 0, 'Message': 'INSUFFICIENT BALANCE'})
        if isinstance(order[-1], dict):
            return_msg = order[-1].get('Message')
            if return_msg != 'Success':
                raise Exception('MOONIX CREATE_ORDER ERROR: ' + str(order[-1]))
            return {'orderId': order[-1].get('OrderId')}
        else:
            raise Exception('MOONIX CREATE_ORDER ERROR: ' + str(order))

    def cancel_order(self, order_id):
        params = [{"orderid":order_id}]
        return self.signed_request('POST', f'/api/cancelorder', payload=params)

    def cancel_all_order(self, pair):
        params = [{"coinpair":pair}]
        return self.signed_request('POST', f'/api/cancelallorder', payload=params)

    def fetch_all_order(self, pair):
        params = [{"coinpair":pair}]
        return self.signed_request('POST', f'/api/openorder', payload=params)

    def fetch_order(self, order_id):
        params = [{"orderid":order_id}]
        order_process = self.signed_request('POST', f'/api/fetchorder', payload=params)
        if isinstance(order_process[-1], dict):
            return order_process[-1].get('Data')

