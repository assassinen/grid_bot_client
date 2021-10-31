import hashlib
import hmac
import time
import json
import requests

API_KEY = 'At880SOrP7kmCq220rtDqTIPHEdQf6BV901UJ9exHiT'
API_SECRET = '662HSheU6XnnafYpQk9Je5AcPYz4SfdO2VwjPVxbRDY'

def _gen_nonce():
  return int(round(time.time() * 1000000))

def generate_auth_headers(API_KEY, API_SECRET, path, body):
  """
  Generate headers for a signed payload
  """
  nonce = str(_gen_nonce())
  signature = "/api/v2/{}{}{}".format(path, nonce, body)
  h = hmac.new(API_SECRET.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
  signature = h.hexdigest()
  return {
    "bfx-nonce": nonce,
    "bfx-apikey": API_KEY,
    "bfx-signature": signature
  }


def post(endpoint, data={}, params=""):
    """
    Send a pre-signed POST request to the bitfinex api
    @return response
    """
    host = 'https://api.bitfinex.com/v2'
    url = '{}/{}'.format(host, endpoint)
    sData = json.dumps(data)
    headers = {"content-type": "application/json"}
    headers.update(generate_auth_headers(API_KEY, API_SECRET, endpoint, sData))
    print(headers)
    return requests.post(url + params, headers=headers, data=sData)


endpoint = 'auth/r/wallets'
endpoint = f'auth/r/orders'
# params = {'limit': 1}
# r = post(endpoint, params)
r = post(endpoint)
print(r.request.headers)
print(r.request.url)
print(r.text)
#
# endpoint = 'auth/w/order/submit'
# body = {'type': 'EXCHANGE LIMIT',
#         'symbol': 'tBTCUSD',
#         'price': '55263',
#         'amount': '0.0001',
#         # 'flags': 0,
#         # 'meta': {'aff_code': "AFF_CODE_HERE"}
# }

# endpoint = 'auth/w/position/increase'
# body = {'symbol': 'tBTCUSD'}
#
endpoint = 'auth/w/order/cancel'
body = {'id': 77333774128}
r = post(endpoint, body)
print(r.request.headers)
print(r.text)


    # async with aiohttp.ClientSession() as session:
    #     async with session.post(url + params, headers=headers, data=sData) as resp:
    #         text = await resp.text()
    #         if resp.status < 200 or resp.status > 299:
    #             raise Exception('POST {} failed with status {} - {}'
    #                             .format(url, resp.status, text))
    #         parsed = json.loads(text, parse_float=self.parse_float)
    #         return parsed

# from binance.exchange import BinanceExchangeCoinFuturesInterface
#
# api_key = ""
# api_secret = ""
# OPTIONS_URL = 'https://dapi.binance.com/dapi'
#
# client = BinanceExchangeCoinFuturesInterface(key=api_key,
#                                    secret=api_secret,
#                                    base_url=OPTIONS_URL,
#                                    api_url="v1",
#                                    # instrument="BTCUSD_PERP",
#                                    instrument="BTCUSD_211231",
#                                              )
#
# # print(client.get_positions())
# # print(client.get_last_order_price('buy'))
# # print(client.get_last_trade_price())
# # print(client.get_open_orders())
# order_id = client.get_open_orders()[0].get('order_id')
# print(order_id)
# print(client.get_order_state(order_id))

# print(client.cancel_all_orders())
# print(client.cancel_order(order_id))
# order = {'side': 'buy',
#          'price': 55000.4,
#          'size': 1}
# print(client.create_order(order))


# from deribit.exchange_v2 import DeribitExchangeInterface
#
# api_key = ""
# api_secret = ""
# URL = 'https://www.deribit.com'
#
# client = DeribitExchangeInterface(key=api_key,
#                                    secret=api_secret,
#                                    base_url=URL,
#                                    api_url="/api/v2/",
#                                    # instrument="BTCUSD_PERP",
#                                    instrument="BTC-29OCT21-70000-C",
#                                              )
# print(client.get_positions())
# # print(client.get_last_order_price('buy'))
# print(client.get_last_trade_price())
# # print(client.get_open_orders())
# # print(client.cancel_all_orders())
# # order = {'side': 'buy',
# #          'price': 3000,
# #          'size': 1}
# # print(client.create_order(order))
