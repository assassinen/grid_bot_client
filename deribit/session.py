
import requests
import time
from models.log import setup_custom_logger

class Session():
    def __init__(self, key, secret, base_url, api_url):
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.api_url = api_url
        self.url = base_url + api_url
        self.access_token = None
        self.refresh_token = None
        self.expires_in = 0
        self.logger = setup_custom_logger(f'session.{self.key}')

    def auth(self):
        method = 'public/auth'
        params = {
            'grant_type': 'client_credentials',
            'client_secret': self.secret,
            'client_id': self.key,
            'scope': 'session:micropython'
        }
        response = self.post(method, params)
        if response:
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            self.expires_in = time.time() + response['expires_in']

    def post(self, method, params):
        url = self.url + method
        headers = {'Content-Type': 'application/json'}
        data = {
            'method': method,
            'params': params
        }
        if method != 'public/auth' and self.expires_in < time.time():
            self.auth()
        if method.startswith('private'):
            headers['Authorization'] = 'Bearer {}'.format(self.access_token)

        try:
            response = requests.post(url=url, headers=headers, json=data)
        except Exception as r:
            self.logger.info(r)

        if response.status_code != 200:
            raise Exception(f"Wrong response code: {response.status_code}",
                            f"{response.text}")

        return response.json()['result']
