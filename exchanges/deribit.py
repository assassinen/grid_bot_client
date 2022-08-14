import time

import requests
from models.states import OrderSide


class DeribitExchangeInterface:
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

    def _auth(self):
        method = 'public/auth'
        params = {
            'grant_type': 'client_credentials',
            'client_secret': self.secret,
            'client_id': self.key,
            'scope': 'session:micropython',
        }
        response = self._post(method, params)
        if response:
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            self.expires_in = time.time() + response['expires_in']

    def _post(self, method, params):
        url = self.url + method
        headers = {'Content-Type': 'application/json'}
        data = {'method': method, 'params': params}
        if method != 'public/auth' and self.expires_in < time.time():
            self._auth()
        if method.startswith('private'):
            headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        try:
            response = requests.post(url=url, headers=headers, json=data)
        except Exception as r:
            self.logger.info(r)
        if response.status_code != 200:
            raise Exception(
                f'Wrong response code: {response.status_code}', f'{response.text}'
            )
        return response.json()['result']

    def get_positions(self):
        method = 'private/get_position'
        params = {'instrument_name': self.instrument}
        result = self._post(method, params)
        return {
            'price': result.get('average_price'),
            'size': result.get('size', 0),
        }

    def get_get_mark_price(self):
        # для опционов
        method = 'public/get_book_summary_by_instrument'
        params = {'instrument_name': self.instrument}
        result = self._post(method, params)
        return result[0]['mark_price'] if result else None

    def get_last_trade_price(self):
        if self.instrument.endswith('C') or self.instrument.endswith('P'):
            return self.get_get_mark_price()
        method = 'public/get_last_trades_by_instrument'
        params = {'instrument_name': self.instrument, 'count': 1}
        result = self._post(method, params)
        return result['trades'][0]['price'] if result else None

    def get_last_order_price(self, side):
        method = 'private/get_order_history_by_instrument'
        params = {'instrument_name': self.instrument, 'count': 1}
        last_order_price = [
            order['price']
            for order in self._post(method, params)
            if order['direction'] == side
        ]
        return (
            last_order_price[0]
            if len(last_order_price) > 0
            else self.get_last_trade_price()
        )

    def get_order_params_from_responce(self, responce):
        return {
            'price': responce.get('price'),
            'size': responce.get('amount'),
            'side': responce.get('direction'),
            'order_id': responce.get('order_id'),
            # 'status': responce.get('order_state'),
            # 'timestamp': responce.get('last_update_timestamp'),
        }

    def get_trade_params_from_responce(self, responce):
        # side = 'buy' if responce[4] > 0 else 'sell'
        # ratio = 1 if responce[4] > 0 else -1
        return {
            'trade_id': responce['trade_id'],
            'price': responce['price'],
            'size': responce['amount'],
            'side': responce['direction'],
            'fee': responce['fee'] * responce['index_price'],
            'fee_currency': 'USD',
            'timestamp': responce['timestamp'],
        }

    def get_trade_params_from_responce(self, responce):
        # side = 'buy' if responce[4] > 0 else 'sell'
        # ratio = 1 if responce[4] > 0 else -1
        return {
            'trade_id': responce['trade_id'],
            'price': responce['price'],
            'size': responce['amount'],
            'side': responce['direction'],
            'fee': responce['fee'] * responce['index_price'],
            'fee_currency': 'USD',
            'timestamp': responce['timestamp'],
        }

    def get_trade_params_from_transaction_log(self, responce):
        return {
            'trade_id': responce['trade_id'],
            'price': responce['price'],
            'size': responce['amount'],
            'side': responce['side'].split()[1],
            'fee': responce['commission'],
            'fee_currency': responce['currency'],
            'timestamp': responce['timestamp'],
        }

    def get_trades(self, last_trade_time):
        endpoint = 'private/get_transaction_log'
        params = {'currency': self.instrument.split('-')[0],
                  'start_timestamp': last_trade_time,
                  'end_timestamp': 	int(time.time() * 1000),
                  'count': 1000}
        trades = self._post(endpoint, params)
        return [
            self.get_trade_params_from_transaction_log(trade)
            for trade in trades.get('logs', [])
            if trade.get('instrument_name') == self.instrument and
               trade.get('type') == 'trade'
        ]

    def get_open_orders(self):
        method = 'private/get_open_orders_by_instrument'
        params = {'instrument_name': self.instrument}
        open_orders = self._post(method, params)
        return [self.get_order_params_from_responce(order) for order in open_orders]

    def get_order_state(self, order_id):
        method = 'private/get_order_state'
        params = {'order_id': order_id}
        try:
            order = self._post(method, params)
        except Exception as err:
            order = {'order_id': order_id, 'order_state': 'cancelled'}
        return self.get_order_params_from_responce(order)

    def get_orders_state(self, orders_state):
        open_orders = self.get_open_orders()
        open_order_ids = [open_order.get('order_id') for open_order in open_orders]
        order_state_ids = [
            order_id for order_id in orders_state if order_id not in open_order_ids
        ]
        return open_orders + [
            self.get_order_state(order_id) for order_id in order_state_ids
        ]

    def create_order(self, order):
        method = 'private/buy' if order['side'] == OrderSide.buy else 'private/sell'
        params = {
            'instrument_name': self.instrument,
            'amount': order['size'],
            'price': order['price'],
            'post_only': 'true',
            'time_in_force': 'good_til_cancelled',
            'type': 'limit',
        }
        order = self._post(method, params)
        return self.get_order_params_from_responce(order.get('order'))

    def cancel_all_orders(self):
        method = 'private/cancel_all_by_instrument'
        params = {'instrument_name': self.instrument, 'type': 'all'}
        result = self._post(method, params)
        return result

    def cancel_order(self, order_id):
        method = 'private/cancel'
        params = {'order_id': order_id}
        result = self._post(method, params)
        return result