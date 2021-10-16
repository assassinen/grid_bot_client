from binance.exchange import BinanceExchangeCoinFuturesInterface

api_key = ""
api_secret = ""
OPTIONS_URL = 'https://dapi.binance.com/dapi'

client = BinanceExchangeCoinFuturesInterface(key=api_key,
                                   secret=api_secret,
                                   base_url=OPTIONS_URL,
                                   api_url="v1",
                                   # instrument="BTCUSD_PERP",
                                   instrument="BTCUSD_211231",
                                             )

# print(client.get_positions())
# print(client.get_last_order_price('buy'))
# print(client.get_last_trade_price())
# print(client.get_open_orders())
order_id = client.get_open_orders()[0].get('order_id')
print(order_id)
print(client.get_order_state(order_id))

# print(client.cancel_all_orders())
# print(client.cancel_order(order_id))
# order = {'side': 'buy',
#          'price': 55000.4,
#          'size': 1}
# print(client.create_order(order))


# from deribit.exchange_v2 import DeribitExchangeInterface
#
# api_key =
# api_secret =
# URL = 'https://www.deribit.com'
#
# client = DeribitExchangeInterface(key=api_key,
#                                    secret=api_secret,
#                                    base_url=URL,
#                                    api_url="/api/v2/",
#                                    # instrument="BTCUSD_PERP",
#                                    instrument="ETH-PERPETUAL",
#                                              )
#
# # print(client.get_positions())
# # print(client.get_last_order_price('buy'))
# # print(client.get_last_trade_price())
# print(client.get_open_orders())
# # print(client.cancel_all_orders())
# order = {'side': 'buy',
#          'price': 3000,
#          'size': 1}
# print(client.create_order(order))
