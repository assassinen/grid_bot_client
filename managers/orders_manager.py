import asyncio
import time

import jsonpickle
import requests

from exchanges.bitfinex import BitfinexExchangeInterface
from exchanges.deribit import DeribitExchangeInterface
from models.log import setup_custom_logger


class OrdersManager:

    def __init__(self, settings):
        self.settings = settings
        self.exchanges = {
            'deribit': DeribitExchangeInterface,
            'bitfinex': BitfinexExchangeInterface,
        }
        self.headers = {'Authorization': f'Bearer {settings.TOKEN}',
                        'Content-Type': 'application/json'}
        self.exchange = self.exchanges[self.settings.EXCHANGE](key=self.settings.API_KEY,
                                                               secret=self.settings.API_SECRET,
                                                               base_url=self.settings.BASE_URL,
                                                               api_url=self.settings.API_URL,
                                                               instrument=self.settings.INSTRUMENT)
        self.logger = setup_custom_logger(f'orders_manager.{self.settings.API_KEY[:8]}')
        self.orders_state = []
        # self.base_url = 'http://grid-bot-server.herokuapp.com/api/v2.0/'
        # self.base_url = 'http://127.0.0.1:5000/api/v2.0/'
        self.base_url = 'http://45.141.102.133:5000/api/v2.0/'
        # self.base_url = 'http://moneyprinter.pythonanywhere.com/api/v2.0/'
        self.orders_calculator_url = f'{self.base_url}orders_calculator_by_{self.settings.strategy}/' \
                                     f'{self.settings.API_KEY}:{self.settings.INSTRUMENT}'
        self.last_trade_time = self.settings.last_trade_time

    def load_settings(self, file):
        with open(f'{file}.json') as f:
            settings = [s for s in jsonpickle.decode(f.read())
                        if s.API_KEY == self.API_KEY]
            return settings[0]

    def get_data_for_calculations(self):
        return {
                'trades': self.exchange.get_trades(self.last_trade_time),
                'last_prices': {'trade_price': self.exchange.get_last_trade_price(),
                                'order_price': self.exchange.get_last_order_price(self.settings.GRID_SIDE)},
                'positions': self.exchange.get_positions(),
                'open_orders': self.exchange.get_open_orders(),
        }

    def replace_orders(self, to_create, to_cancel):
        orders_status = []
        if len(to_cancel) > 0:
            self.logger.info("Canceling %d orders:" % (len(to_cancel)))
            for order in to_cancel:
                try:
                    self.exchange.cancel_order(order)
                    self.logger.info(f"  {order}")
                except Exception as err:
                    self.logger.info(f"cancelling order error: {err}")
            time.sleep(0.001)
        if len(to_create) > 0:
            self.logger.info("Creating %d orders:" % (len(to_create)))
            for order in to_create:
                try:
                    responce = self.exchange.create_order(order)
                    orders_status.append(responce.get('order_id'))
                    self.logger.info("  %4s %.5f @ %.4f" % (
                        responce.get('side'), responce.get('size'), responce.get('price')))
                except Exception as err:
                    self.logger.info(f"added order error: {err}")
            time.sleep(0.001)
        return orders_status


    def get_orders_for_update(self, kw):
        orders_for_update = requests.post(url=self.orders_calculator_url, headers=self.headers, json=kw)
        try:
            status_code = orders_for_update.status_code
            result = orders_for_update.json()
            if status_code == 400 and result == 'exchange_settings not found':
                self.logger.info(f'result: {result}')
                raise SetSettings(
                    f'the exchange_settings will be available in the next iteration'
                )
            elif status_code == 200:
                return orders_for_update.json()
            else:
                raise SetSettings(
                    f'status_code: {status_code} '
                    f'response: {orders_for_update.text}'
                )
        except Exception as err:
            raise err

    def check_position_size(self, kw):
        active_orders = kw.get('active_orders')
        active_orders_size = sum([order.get('size') for order in active_orders
                                  if order.get('side') == self.settings.REVERSE_SIDE])
        return active_orders_size <= kw.get('positions').get('size')

    async def run_loop(self):
        while True:
            try:
                kw = self.get_data_for_calculations()

                # self.logger.info(f"last_prices: {kw.get('last_prices')}")
                # self.logger.info(f"positions: {kw.get('positions')}")
                # time.sleep(0.001)
                # self.logger.info("open_orders: ")
                # time.sleep(0.001)
                # for order in kw.get("open_orders"):
                #     self.logger.info(f"  {order}")
                # time.sleep(0.001)
                # self.logger.info("trades: ")
                # time.sleep(0.001)
                # for trade in kw.get("trades"):
                #     self.logger.info(f"  {trade}")
                # time.sleep(0.001)

                # print(len(kw['trades']))
                # for i in kw['trades']:
                #     print(i)

                orders_for_update = self.get_orders_for_update(kw)
                for k, v in orders_for_update.items():
                    self.logger.info(f"{k}: ")
                    if k == 'last_db_trade_time':
                        time.sleep(0.001)
                        self.logger.info(f"  {v}")
                        time.sleep(0.001)
                    else:
                        for order in v:
                            self.logger.info(f"  {order}")
                        time.sleep(0.001)

                self.last_trade_time = orders_for_update.get('last_db_trade_time', self.last_trade_time)
                time.sleep(0.001)
                # self.replace_orders(orders_for_update.get('to_create'),
                #                     orders_for_update.get('to_cancel'))
            except Exception as err:
                self.logger.info(f"{err}")
            await asyncio.sleep(self.settings.LOOP_INTERVAL)


class SetSettings(Exception):
    pass