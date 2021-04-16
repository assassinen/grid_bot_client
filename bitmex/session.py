import requests
import time
import json
import hmac
import hashlib
from models.log import setup_custom_logger

class Session():

    def __init__(self, key, secret, base_url, api_url):
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.api_url = api_url
        self.logger = setup_custom_logger(f'session.{self.key}')

    def generate_signature(self, expires, metod, path, data=None):
        """Generate a request signature compatible with BitMEX."""
        data = json.dumps(data) if data else ''
        message = metod + path + str(expires) + data
        signature = hmac.new(bytes(self.secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def get_headers(self, metod, path, data=''):
        expires = int(time.time()) + 5
        headers = {}
        headers['api-expires'] = str(expires)
        headers['api-key'] = self.key
        headers['api-signature'] = self.generate_signature(expires, metod, path, data)
        return headers

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
            raise Exception(f"Wrong response code: {response.status_code} "
                            f"Text: {response.text}")
        return response.json()

    def get(self, action, query=''):
        return self.request('GET', action, query)

    def post(self, action, postdict):
        return self.request('POST', action, data=postdict)

    def delete(self, action, postdict):
        return self.request('DELETE', action, data=postdict)

