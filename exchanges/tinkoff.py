import time
import pytz
from datetime import datetime, timedelta
import requests
from models.states import OrderSide
from models.log import setup_custom_logger


class TinkoffExchangeInterface:

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
        self.figi, self.lot = self.get_figi()
        self.logger = setup_custom_logger(f'tinkoff_exchange.{self.key[:8]}')

    def request(self, metod, endpoint, data={}, params=""):
        url = self.url + endpoint
        headers = {'Content-Type': 'application/json',
                   "Authorization": f"Bearer {self.secret}"}
        try:
            if metod == 'GET':
                response = requests.get(url=url, headers=headers, json=data, params=params)
            if metod == 'POST':
                # sData = json.dumps(data)
                # headers.update(self.generate_auth_headers(endpoint, sData))
                response = requests.post(url=url, headers=headers, json=data)
        except Exception as r:
            self.logger.info(r)
        if response.status_code != 200:
            raise Exception(f"Wrong response code: {response.status_code}",
                            f"{response.request.url}",
                            f"{response.request.body}",
                            f"{response.text}")
        return response.json().get('payload')

    def _post(self, endpoint, data={}, params=""):
        return self.request('POST', endpoint, data=data, params=params)

    def _get(self, endpoint, data={}, params=""):
        return self.request('GET', endpoint, data=data, params=params)

    def get_date(self):
        _to = datetime.now(pytz.timezone("Europe/Moscow"))
        _from = _to - timedelta(days=7)
        return _from.isoformat(), _to.isoformat()

    def get_figi(self):
        method = '/market/search/by-ticker'
        params = {'ticker': self.instrument}
        result = self._get(method, params=params).get('instruments', [])
        return result[0].get('figi'), result[0].get('lot') if len(result) > 0 else None

    def get_positions(self):
        method = '/portfolio'
        try:
            result = self._get(method)
            position = [position for position in result.get('positions')
                        if position.get('ticker') == self.instrument]
            position = {'average_price': position[0]['averagePositionPrice']['value'],
                        'size': position[0].get('balance', 0)}
        except Exception as err:
            self.logger.info(err)
            position = {'average_price': None, 'size': 0}
        return position

    def get_last_trade_price(self):
        method = '/market/orderbook'
        params = {'figi': self.figi,
                  'depth': 1}
        result = self._get(method, params=params)
        return result.get('lastPrice') if result else None

    def get_last_order_price(self, side):
        method ='/operations'
        _from, _to = self.get_date()
        params = {'from': _from,
                  'to': _to,
                  'figi': self.figi}
        result = self._get(method, params=params)
        last_order_price = [order.get('price') for order
                            in result.get('operations', [])
                            if order.get('operationType').lower() == side]
        return last_order_price[0] if len(last_order_price) > 0 else self.get_last_trade_price()

    def get_order_params_from_responce(self, responce):
        status_mapp = {'New': 'open', 'Decline': 'cancelled', 'Done': 'filled'}
        data_format = '%Y-%m-%dT%H:%M:%S.%f+03:00'
        dt = responce.get('timestamp', '1970-01-01T00:00:00.000000+03:00')
        _timestamp = int(time.mktime(datetime.strptime(dt, data_format).timetuple()) * 1000)

        return {'price': responce.get('price'),
                'size': responce.get('requestedLots'),
                'side': responce.get('operation', '').lower(),
                'order_id': responce.get('orderId'),
                'status': status_mapp.get(responce.get('status')),
                'timestamp': _timestamp}

    def get_open_orders(self):
        method = '/orders'
        try:
            open_orders = [position for position in self._get(method)
                           if position.get('figi') == self.figi]
        except Exception as err:
            self.logger.warning(err)
            open_orders = [{}]
        return [self.get_order_params_from_responce(order) for order in open_orders]

    # def get_order_state(self, order_id):
    #     method ='/operations'
    #     _from, _to = self.get_date()
    #     params = {'from': _from,
    #               'to': _to,
    #               'figi': self.figi}
    #     result = self._get(method, params=params)
    #     orders = [order.get('price') for order
    #               in result.get('operations', [])
    #               if order.get('operationType').lower() == side]
    #     method = 'private/get_order_state'
    #     return
    #     # return self.get_order_params_from_responce(order)

    def get_orders_state(self, orders_state):
        # open_orders = self.get_open_orders()
        # open_order_ids = [open_order.get('order_id') for open_order in open_orders]
        # order_state_ids = [order_id for order_id in orders_state if order_id not in open_order_ids]

        method ='/operations'
        _from, _to = self.get_date()
        params = {'from': _from,
                  'to': _to,
                  'figi': self.figi}
        result = self._get(method, params=params)
        orders = [self.get_order_params_from_responce({'price': order.get('price'),
                                                       'requestedLots': order.get('quantity') / self.lot,
                                                       'operation': order.get('operationType').lower(),
                                                       'orderId': order.get('id'),
                                                       'status': order.get('status'),
                                                       'timestamp': order.get('date')
                                                       })
                  for order in result.get('operations', [])
                  if order.get('id') in orders_state]
        return self.get_open_orders() + orders

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
