import hashlib
import hmac
import json
import threading
import time

import requests
import websocket

from models.log import setup_custom_logger


class APIKeyAuth:

    def generate_signature(self, expires, metod, path, data=None):
        """Generate a request signature compatible with BitMEX."""
        data = json.dumps(data) if data else ''
        message = metod + path + str(expires) + data
        signature = hmac.new(bytes(self.secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def get_headers(self, metod, path, data=''):
        expires = int(time.time() + 5)
        headers = {}
        headers['api-expires'] = str(expires)
        headers['api-key'] = self.key
        headers['api-signature'] = self.generate_signature(expires, metod, path, data)
        return headers


class Session(APIKeyAuth):

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.api_url = api_url
        self.logger = setup_custom_logger(f'session.{self.key}')
        self.ws = BitmexWebsocket(key, secret, base_url, instrument)

    def request(self, metod, action, query='', data=''):
        path = self.api_url + action + query
        url = self.base_url + path
        headers = self.get_headers(metod, path, data)
        try:
            if metod == 'GET':
                response = requests.get(url=url, headers=headers)
            if metod == 'POST':
                response = requests.post(url=url, headers=headers, json=data)
            if metod == 'DELETE':
                response = requests.delete(url=url, headers=headers, json=data)
        except Exception as r:
            self.logger.info(r)

        if response.status_code != 200:
            raise Exception("Wrong response code: {0}".format(response.status_code))
        return response.json()


    def get(self, action, query=''):
        return self.request('GET', action, query)

    def post(self, action, postdict):
        return self.request('POST', action, data=postdict)

    def delete(self, action, postdict):
        return self.request('DELETE', action, data=postdict)

    def get_position_from_ws(self):
        return self.ws.position()

    def get_last_trade_from_ws(self):
        return self.ws.recent_trades()

    def get_open_orders_from_ws(self):
        return self.ws.open_orders()


class BitmexWebsocket(Session):

    MAX_TABLE_LEN = 20

    def __init__(self, key, secret, base_url, symbol):
        self.__reset()
        self.key = key
        self.secret = secret
        self.symbol = symbol
        self.base_url = base_url
        self.connect()
        self.logger = setup_custom_logger(f'bitmex_websocket.{self.key}')

    def connect(self):
        subscriptions = [f'trade:{self.symbol}',
                         f'order:{self.symbol}',
                         f'position:{self.symbol}']
        ws_url = self.base_url.replace('http', 'ws') + "/realtime?subscribe=" + ",".join(subscriptions)
        self.ws = websocket.WebSocketApp(url=ws_url,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth()
                                         )
        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()

    def position(self):
        positions = self.data['position']
        pos = [p for p in positions if p['symbol'] == self.symbol]
        if len(pos) == 0:
            return {'avgCostPrice': 0, 'avgEntryPrice': 0, 'currentQty': 0, 'symbol': self.symbol}
        return pos

    def recent_trades(self):
        return sorted(self.data['trade'], key=lambda x: x['timestamp'], reverse=True)

    def open_orders(self):
        orders = self.data['order']
        return [o for o in orders if o['leavesQty'] is not None and o['leavesQty'] > 0]

    def __on_message(self, ws, message):
        message = json.loads(message)
        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None

        try:
            if action:
                if table not in self.data:
                    self.data[table] = []

                if table not in self.keys:
                    self.keys[table] = []

                if action == 'partial':
                    self.data[table] += message['data']

                elif action == 'insert':
                    self.data[table] += message['data']
                    if table not in ['order', 'orderBookL2'] and len(self.data[table]) > BitmexWebsocket.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][(BitmexWebsocket.MAX_TABLE_LEN // 2):]

                elif action == 'update':
                    for updateData in message['data']:
                        item = self.findItemByKeys(self.keys[table], self.data[table], updateData)
                        if not item:
                            continue  # No item found to update. Could happen before push

                        item.update(updateData)

                        if table == 'order' and item['leavesQty']is not None and item['leavesQty'] <= 0:
                            self.data[table].remove(item)

                elif action == 'delete':
                    for deleteData in message['data']:
                        item = self.findItemByKeys(self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("unknown action: %s" % action)

        except Exception as r:
            raise Exception(r)

    def __on_close(self, ws):
        self.logger.info("websocket closed")

    def __on_open(self, ws):
        self.logger.info("websocket opened")

    def __on_error(self, ws, message):
        raise Exception("web socket error: {0}".format(message))

    def __get_auth(self):
        headers = self.get_headers(metod='GET', path='/realtime', data='')
        return [f'{k}: {v}' for k, v in headers.items()]

    def __reset(self):
        # self.data = {'trade': {}, 'order': {}, 'position': {}}
        self.data = {}
        self.keys = {}


    def findItemByKeys(self, keys, table, matchData):
        for item in table:
            matched = True
            for key in keys:
                if item[key] != matchData[key]:
                    matched = False
            if matched:
                return item
