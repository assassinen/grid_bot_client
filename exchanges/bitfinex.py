import hashlib
import hmac
import time
import json
import requests
from models.log import setup_custom_logger

class BitfinexExchangeInterface:

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.api_url = api_url
        self.url = base_url + api_url
        self.access_token = None
        self.refresh_token = None
        self.expires_in = 0
        self.instrument = instrument
        self.logger = setup_custom_logger(f'bitfinex_exchange.{self.key}')

    def generate_auth_headers(self, path, body):
        """
        Generate headers for a signed payload
        """
        nonce = str(int(round(time.time() * 1000000)))
        signature = "/api/v2/{}{}{}".format(path, nonce, body)
        h = hmac.new(self.secret.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
        signature = h.hexdigest()
        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.key,
            "bfx-signature": signature
        }

    def request(self, metod, endpoint, data={}, params=""):
        """
        Send a pre-signed POST request to the bitfinex api
        @return response
        """
        url = '{}/{}'.format(self.url, endpoint)
        headers = {"content-type": "application/json"}
        try:
            if metod == 'GET':
                response = requests.get(url=url, headers=headers, json=data)
            if metod == 'POST':
                sData = json.dumps(data)
                headers.update(self.generate_auth_headers(endpoint, sData))
                response = requests.post(url=url, headers=headers, json=data)
        except Exception as r:
            self.logger.info(r)
        if response.status_code != 200:
            raise Exception(f"Wrong response code: {response.status_code}",
                            f"{response.request.url}",
                            f"{response.request.body}",
                            f"{response.text}")
        if endpoint == f'auth/r/orders/{self.instrument}/hist':
            self.logger.debug(response.request.url)
            self.logger.debug(response.request.body)
            self.logger.debug(response.json())
        return response.json()

    def _post(self, endpoint, data={}, params=""):
        return self.request('POST', endpoint, data=data, params=params)

    def _get(self, endpoint, data={}, params=""):
        return self.request('GET', endpoint, data=data, params=params)

    def get_positions(self):
        endpoint = 'auth/r/wallets'
        wallet = [wallet for wallet in self._post(endpoint) if wallet[0] == 'exchange' and wallet[1] == 'BTC']
        wallet = wallet[0] if len(wallet) > 0 else wallet
        size = round(wallet[2], 10) if len(wallet) > 0 else 0
        return {'price': self.get_last_trade_price(), 'size': size}

    def get_last_trade_price(self):
        endpoint = f'trades/{self.instrument}/hist'
        params = {'limit': 1}
        return self._get(endpoint, params)[0][3]

    def get_last_order_price(self, side):
        endpoint = f'auth/r/trades/{self.instrument}/hist'
        if side == 'buy':
            last_order_price = [i[5] for i in self._post(endpoint) if i[4] > 0]
        else:
            last_order_price = [i[5] for i in self._post(endpoint) if i[4] > 0]
        return last_order_price[0] if len(last_order_price) > 0 else self.get_last_trade_price()

    def get_open_orders(self):
        method = f'auth/r/orders/{self.instrument}'
        open_orders = self._post(method)
        return [self.get_order_params_from_responce(order) for order in open_orders]

    def get_trade_params_from_responce(self, responce):
        side = 'buy' if responce[4] > 0 else 'sell'
        ratio = 1 if responce[4] > 0 else -1
        return {'trade_id': responce[0],
                'price': responce[5],
                'size': responce[4] * ratio,
                'side': side,
                'fee': float(responce[9]) * -1,
                'fee_currency': responce[10],
                'timestamp': responce[2]
                }


    def get_trades(self, last_trade_time):
        endpoint = f'auth/r/trades/{self.instrument}/hist'
        params = {
            'start': last_trade_time,
            'limit': 1000,
            'sort': 1
        }
        trades = self._post(endpoint, params)
        return [self.get_trade_params_from_responce(trade) for trade in trades]

    def get_order_state(self, order_id):
        method = f'auth/r/orders/{self.instrument}/hist'
        params = {'id': [order_id]}
        order = self._post(method, params)
        return self.get_order_params_from_responce(order[0]) if len(order) > 0 \
            else {'order_id': order_id, 'order_state': 'cancelled'}


    def replace_order_status(self, raw_status):
        status_mapp = {'ACTIVE': 'open', 'CANCELED': 'cancelled'}
        if 'EXECUTED' in raw_status:
            status = 'filled'
        else:
            status = status_mapp.get(raw_status, None)
        if status is None:
            self.logger.info(f'invalid status: {raw_status}')
        return status

    def get_order_params_from_responce(self, responce):
        side = 'buy' if responce[7] > 0 else 'sell'
        ratio = 1 if responce[7] > 0 else -1
        return {'price': responce[16],
                'size': responce[7] * ratio,
                'side': side,
                'order_id': str(responce[0]),
                # 'status': self.replace_order_status(responce[13]),
                # 'timestamp': responce[5]
                }

    def create_order(self, order):
        ratio = 1 if order['side'] == 'buy' else -1
        method = f'auth/w/order/submit'
        params = {'type': 'EXCHANGE LIMIT',
                  'symbol': self.instrument,
                  'price': str(order['price']),
                  'amount': str(order['size'] * ratio)
                  }
        result = self._post(method, params)
        if 'SUCCESS' in result:
            return [self.get_order_params_from_responce(orders) for orders in result[4]][0]

    def cancel_order(self, order_id):
        method = f'auth/w/order/cancel'
        params = {'id': int(order_id)}
        result = self._post(method, params)
        return result[4][0]
        # if 'SUCCESS' in result:
        #     order_id = result[4][0]
        #     return self.get_order_state(order_id)
