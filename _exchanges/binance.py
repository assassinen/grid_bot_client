import time
import json
import hmac
import hashlib
import requests
from operator import itemgetter
from datetime import datetime


class BinanceAPIException(Exception):

    def __init__(self, response, status_code, text):
        self.code = 0
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)


class BinanceRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message


class BinanceExchangeBaseInterface:

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.instrument = instrument
        self.API_KEY = key
        self.API_SECRET = secret
        self.uri = f'{base_url}/{api_url}'
        self.session = self._init_session()

    def _get_headers(self):
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',  # noqa
        }
        if self.API_KEY:
            assert self.API_KEY
            headers['X-MBX-APIKEY'] = self.API_KEY
        return headers

    def _init_session(self):
        headers = self._get_headers()
        session = requests.session()
        session.headers.update(headers)
        return session

    def _request(self, method, uri, signed, force_params=False, **kwargs):
        kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)
        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(self.response)

    @staticmethod
    def _handle_response(response: requests.Response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not (200 <= response.status_code < 300):
            raise BinanceAPIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)

    @staticmethod
    def _order_params(data):
        """Convert params to list with signature as last element

        :param data:
        :return:

        """
        data = dict(filter(lambda el: el[1] is not None, data.items()))
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, str(value)))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _get_request_kwargs(self, method, signed: bool, force_params: bool = False, **kwargs):
        # set default requests timeout
        self.REQUEST_TIMEOUT = 10
        self.timestamp_offset = 0
        # kwargs['timeout'] = self.REQUEST_TIMEOUT

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del(kwargs['data']['requests_params'])

        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000 + self.timestamp_offset)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        # sort get and post params to match signature order
        if data:
            # sort post params and remove any arguments with values of None
            kwargs['data'] = self._order_params(kwargs['data'])
            # Remove any arguments with values of None.
            null_args = [i for i, (key, value) in enumerate(kwargs['data']) if value is None]
            for i in reversed(null_args):
                del kwargs['data'][i]

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del(kwargs['data'])

        return kwargs

    def _generate_signature(self, data) -> str:
        ordered_data = self._order_params(data)
        query_string = '&'.join([f"{d[0]}={d[1]}" for d in ordered_data])
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()


class BinanceExchangeVanillaOptionsInterface(BinanceExchangeBaseInterface):

    def get_positions(self):
        path = 'position'
        params = {"symbol": self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        position = [i for i in result.get('data') if i.get('symbol') == self.instrument]
        position = position[0] if len(position) > 0 else {}
        return {'average_price': position.get('entryPrice'),
                'size': position.get('quantity', 0)}

    def get_last_trade_price(self):
        path = 'ticker'
        params = {"symbol": self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        price = [i for i in result.get('data') if i.get('symbol') == self.instrument]
        return price[0].get('lastPrice') if len(price) > 0 else None

    def get_last_order_price(self, side):
        path = 'userTrades'
        params = {'symbol': self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        price = [i for i in result.get('data') if i.get('symbol') == self.instrument]
        return price[0].get('price') if len(price) > 0 else self.get_last_trade_price()

    def get_order_state(self, order_id):
        # todo реализовать
        try:
            1 / 0
            order = {}
        except Exception as r:
            order = {'orderID': order_id, 'ordStatus': 'cancelled'}
        return self._get_order_params_from_responce(order)

    def get_open_orders(self):
        path = 'openOrders'
        params = {'symbol': self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        open_orders = [i for i in result.get('data') if i.get('symbol') == self.instrument]
        return [self._get_order_params_from_responce(order) for order in open_orders]

    def get_orders_state(self, orders_state):
        open_orders = self.get_open_orders()
        open_order_ids = [open_order.get('order_id') for open_order in open_orders]
        order_state_ids = [order_id for order_id in orders_state if order_id not in open_order_ids]
        return open_orders + [self.get_order_state(order_id) for order_id in order_state_ids]

    def create_order(self, order=''):
        postdict = {
            'symbol': self.instrument,
            'side': order['side'].title(),
            'orderQty': order['size'],
            'price': order['price'],
            'ordType': 'Limit',
            'execInst': 'ParticipateDoNotInitiate'}
        order = self.session.post('order', postdict)
        return self._get_order_params_from_responce(order)

    def cancel_all_orders(self):
        # todo реализовать
        postdict = {'symbol': self.instrument}
        return self.session.delete('order/all', postdict)


class BinanceExchangeCoinFuturesInterface(BinanceExchangeBaseInterface):

    def get_positions(self):
        path = 'positionRisk'
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data={})
        position = [i for i in result if i.get('symbol') == self.instrument]
        position = position[0] if len(position) > 0 else {}
        return {'average_price': float(position.get('entryPrice')),
                'size': float(position.get('positionAmt', 0))}

    def get_last_trade_price(self):
        path = 'ticker/24hr'
        params = {"symbol": self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        return float(result[0].get('lastPrice')) if len(result) > 0 else None

    def get_last_order_price(self, side):
        path = 'userTrades'
        params = {'symbol': self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        price = [i for i in result if i.get('side') == side.upper()]
        return float(price[-1].get('price')) if len(price) > 0 else self.get_last_trade_price()

    def get_order_state(self, order_id):
        try:
            path = 'order'
            params = {'symbol': self.instrument,
                      'orderId': order_id}
            order = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        except Exception as r:
            order = {'orderID': order_id, 'ordStatus': 'cancelled'}
        return self.get_order_params_from_responce(order)

    def get_order_params_from_responce(self, responce):
        status_mapp = {'NEW': 'open', 'CANCELED': 'cancelled'}
        return {'price': float(responce.get('price')),
                'size': float(responce.get('origQty')),
                'side': responce.get('side', 'No data').lower(),
                'order_id': str(responce.get('orderId')),
                'status': status_mapp.get(responce.get('status'), responce.get('status').lower()),
                'timestamp': responce.get('updateTime'),
                }

    def get_open_orders(self):
        path = 'openOrders'
        params = {'symbol': self.instrument}
        result = self._request('get', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        return [self.get_order_params_from_responce(order) for order in result]

    def get_orders_state(self, orders_state):
        open_orders = self.get_open_orders()
        open_order_ids = [open_order.get('order_id') for open_order in open_orders]
        order_state_ids = [order_id for order_id in orders_state if order_id not in open_order_ids]
        return open_orders + [self.get_order_state(order_id) for order_id in order_state_ids]

    def create_order(self, order=''):
        path = 'order'
        params = {
            'symbol': self.instrument,
            'side': order['side'].upper(),
            'quantity': order['size'],
            'price': order['price'],
            'type': 'LIMIT',
            'timeInForce': 'GTC',
        }
        order = self._request('post', f'{self.uri}/{path}', signed=True, force_params=True, data=params)
        return self.get_order_params_from_responce(order)

    def cancel_all_orders(self):
        path = 'allOpenOrders'
        params = {'symbol': self.instrument}
        return self._request('delete', f'{self.uri}/{path}', signed=True, force_params=True, data=params)

    def cancel_order(self, order_id):
        path = 'order'
        params = {'symbol': self.instrument,
                  'orderId': order_id}
        return self._request('delete', f'{self.uri}/{path}', signed=True, force_params=True, data=params)