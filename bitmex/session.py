from bitmex.generate_signature import generate_signature
import requests


class Session():

    def __init__(self, key, secret, base_url, api_url):
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.api_url = api_url

    def get_headers(self, metod, path, data=''):
        r = requests.get('http://www.direct-time.ru/track.php?id=time_utc')
        expires = int(r.text[:-3]) + 5
        headers = {}
        headers['api-expires'] = str(expires)
        headers['api-key'] = self.key
        headers['api-signature'] = \
            generate_signature(self.secret, expires, metod, path, data)
        return headers

    def request(self, metod, action, query='', data=''):
        path = self.api_url + action + query
        url = self.base_url + path
        headers = self.get_headers(metod, path, data)
        if metod == 'GET':
            response = requests.get(url=url, headers=headers)
        if metod == 'POST':
            response = requests.post(url=url, headers=headers, json=data)
        if metod == 'DELETE':
            response = requests.delete(url=url, headers=headers, json=data)

        if response.status_code != 200:
            raise Exception("Wrong response code: {0}".format(response.status_code))
        json = response.json()

        # if "error" not in json:
        #     if isinstance(json, list):
        #         return json[0]
        #     else:
        #         return json
        # else:
        #     return json
        return json

    def get(self, action, query=''):
        return self.request('GET', action, query)

    def post(self, action, postdict):
        return self.request('POST', action, data=postdict)

    def delete(self, action, postdict):
        return self.request('DELETE', action, data=postdict)