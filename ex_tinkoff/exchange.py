import json
import random
import time

import requests
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By


class TinkoffExchangeInterface:

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.key = key
        self.base_url = base_url
        self.api_url = api_url
        self.secret = secret
        self.instrument = instrument
        self.ttl_session_id = 60 * 1
        self.srart_time = int(time.time())
        self.session_id_file = 'settings/tcs_session_id.json'
        self.sender_thread = threading.Thread(target=self.simulation)
        self.sender_thread.daemon = True
        self.distinct_session_id = False
        self.driver = webdriver.Remote(command_executor='http://0.0.0.0:4444/wd/hub',
                                       desired_capabilities={"browserName": "chrome",
                                                             "enableVNC": True})
        self.session_id = self.get_session_id()

    def request(self, metod, endpoint, data={}, params=""):
        url = f'{self.base_url}{self.api_url}{endpoint}'
        params = {'sessionId': self.session_id}
        headers = {
            'authority': 'www.tinkoff.ru',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36',
            'content-type': 'application/json',
            'accept': '*/*',
            'origin': 'https://www.tinkoff.ru',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.tinkoff.ru/invest/orders/',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        try:
            if metod == 'GET':
                response = requests.get(url=url, headers=headers, json=data, params=params)
            if metod == 'POST':
                response = requests.post(url=url, headers=headers, json=data, params=params)
        except Exception as r:
            print(r)
            # self.logger.info(r)
        if response.status_code != 200:
            raise Exception(f"Wrong response code: {response.status_code}",
                            f"{response.request.url}",
                            f"{response.request.body}",
                            f"{response.text}")
        print(response.json().get('payload'))
        return response.json().get('payload')

    def _post(self, endpoint, data={}, params=""):
        return self.request('POST', endpoint, data=data, params=params)

    def _get(self, endpoint, data={}, params=""):
        return self.request('GET', endpoint, data=data, params=params)

    def simulation(self):
        while self.distinct_session_id:
            sleep = random.randint(5, 15)
            time.sleep(sleep)
            items = ['Акции', 'Фонды', 'Облигации', 'Валюта', 'Избранное']
            self.driver.find_element(By.LINK_TEXT, items[random.randint(0, 4)]).click()
            data = {'time': int(time.time()), 'session_id': self.session_id}
            with open(self.session_id_file, 'w') as f:
                json.dump(data, f)

    def get_new_session_id(self):
        items = ['Акции', 'Фонды', 'Облигации', 'Валюта', 'Избранное']
        self.driver.get("https://www.tinkoff.ru/invest/catalog")
        time.sleep(5)
        try:
            self.driver.find_element(By.LINK_TEXT, "Войти").click()
            self.driver.find_element(By.NAME, "login").click()
            self.driver.find_element(By.NAME, "login").send_keys(self.key)
            self.driver.find_element(By.NAME, "password").send_keys(self.secret)
            self.driver.find_element(By.CSS_SELECTOR, ".ui-button").click()
            time.sleep(5)
        except Exception as r:
            print(r)
            # self.logger.info(r)
        self.driver.find_element(By.LINK_TEXT, items[random.randint(0, 4)]).click()
        cookies = self.driver.get_cookies()
        self.session_id = [cookie.get('value') for cookie in cookies if cookie.get('name') == 'psid']
        return self.session_id[0] if len(self.session_id) > 0 else ''

    def get_session_id(self):
        with open(self.session_id_file) as f:
            data = json.load(f)
            if data.get('time') + self.ttl_session_id > int(time.time()) and data.get('time') > self.srart_time:
                return data.get('session_id')
            else:
                self.distinct_session_id = False
        data = {'time': int(time.time()), 'session_id': self.get_new_session_id()}
        with open(self.session_id_file, 'w') as f:
            json.dump(data, f)
        self.distinct_session_id = True
        self.sender_thread.start()
        return data.get('session_id')

    def get_open_orders(self):
        metod = '/user/orders'
        return self._post(metod)
        # result = self._post_(metod, referer, data={})
        # orders = result['payload'] if result.get('payload') is not None else {}
        # return orders['orders'] if orders.get('orders') is not None else {}

    def create_order(self, order):
        metod = 'order/limit_order'
        referer = f"https://www.tinkoff.ru/invest/etfs/{order.get('ticker')}/{order.get('side')}/"
        return self._post(metod, referer, order)