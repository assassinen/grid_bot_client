from models.states import OrderSide
from ex_deribit.session import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import time
from selenium.common.exceptions import NoSuchElementException

class TinkoffExchangeInterface:

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.key = key
        self.secret = secret
        self.instrument = instrument
        self.session = Session(key, secret, base_url, api_url)
        self.driver = webdriver.Remote(command_executor='http://0.0.0.0:4444/wd/hub',
                                       desired_capabilities={"browserName": "chrome",
                                                             "enableVNC": True})

    def get_session_id(self):
        items = ['Акции', 'Фонды', 'Облигации', 'Валюта', 'Избранное']
        self.driver.get("https://www.tinkoff.ru/invest/catalog")
        try:
            self.driver.find_element(By.LINK_TEXT, "Войти").click()
            self.driver.find_element(By.NAME, "login").click()
            self.driver.find_element(By.NAME, "login").send_keys(self.key)
            self.driver.find_element(By.NAME, "password").send_keys(self.secret)
            self.driver.find_element(By.CSS_SELECTOR, ".ui-button").click()
            time.sleep(5)
        except:
            pass
        self.driver.find_element(By.LINK_TEXT, items[random.randint(0, 4)]).click()
        cookies = self.driver.get_cookies()
        self.session_id = [cookie.get('value') for cookie in cookies if cookie.get('name') == 'psid']
        return self.session_id[0] if len(self.session_id) > 0 else ''

    def get_positions(self):
        method = 'private/get_position'
        params = {'instrument_name': self.instrument}
        result = self.session.post(method, params)
        return {'average_price': result.get('average_price'),
                'size': result.get('size', 0)}

    def get_last_trade_price(self):
        method = 'public/get_last_trades_by_instrument'
        params = {'instrument_name': self.instrument, 'count': 1}
        result = self.session.post(method, params)
        return result['trades'][0]['price'] if result else None

    def get_last_order_price(self, side):
        method = 'private/get_order_history_by_instrument'
        params = {'instrument_name': self.instrument, 'count': 1}
        last_order_price = [order['price'] for order
                            in self.session.post(method, params)
                            if order['direction'] == side]
        return last_order_price[0] if len(last_order_price) > 0 else self.get_last_trade_price()

    def get_order_params_from_responce(self, responce):
        return {'price': responce.get('price'),
                'size': responce.get('amount'),
                'side': responce.get('direction'),
                'order_id': responce.get('order_id'),
                'status': responce.get('order_state'),
                'timestamp': responce.get('last_update_timestamp')}

    def get_open_orders(self):
        method = 'private/get_open_orders_by_instrument'
        params = {'instrument_name': self.instrument}
        open_orders = self.session.post(method, params)
        return [self.get_order_params_from_responce(order) for order in open_orders]

    def get_order_state(self, order_id):
        method = 'private/get_order_state'
        params = {'order_id': order_id}
        try:
            order = self.session.post(method, params)
        except Exception as err:
            order = {'order_id': order_id, 'order_state': 'cancelled'}
        return self.get_order_params_from_responce(order)

    def get_orders_state(self, orders_state):
        open_orders = self.get_open_orders()
        open_order_ids = [open_order.get('order_id') for open_order in open_orders]
        order_state_ids = [order_id for order_id in orders_state if order_id not in open_order_ids]
        return open_orders + [self.get_order_state(order_id) for order_id in order_state_ids]

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
        order = self.session.post(method, params)
        # print(order)
        return self.get_order_params_from_responce(order.get('order'))

    def cancel_all_orders(self):
        method = 'private/cancel_all_by_instrument'
        params = {'instrument_name': self.instrument, 'type': 'all'}
        result = self.session.post(method, params)
        return result

    def cancel_order(self, order_id):
        method = 'private/cancel'
        params = {'order_id': order_id}
        result = self.session.post(method, params)
        return result
