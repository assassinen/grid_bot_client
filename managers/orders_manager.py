import asyncio
import os.path
import requests
import jsonpickle
from bitmex.exchange import BitmexExchangeInterface
from deribit.exchange_v2 import DeribitExchangeInterface
from models.log import setup_custom_logger


class OrdersManager:

    def __init__(self, settings):
        self.settings = settings
        self.exchanges = {
            'bitmex': BitmexExchangeInterface,
            'deribit': DeribitExchangeInterface
        }
        self.exchange = self.exchanges[self.settings.EXCHANGE](key=self.settings.API_KEY,
                                                               secret=self.settings.API_SECRET,
                                                               base_url=self.settings.BASE_URL,
                                                               api_url=self.settings.API_URL,
                                                               instrument=self.settings.SYMBOL)
        self.logger = setup_custom_logger(f'orders_manager.{self.settings.API_KEY}')
        self.orders_state = []
        self.base_url = 'http://moneyprinter.pythonanywhere.com/api/v1.0/'
        # self.base_url = 'http://127.0.0.1:5000/api/v1.0/'
        self.orders_calculator_url = f'{self.base_url}orders_calculator/{self.settings.API_KEY}:{self.settings.SYMBOL}'
        self.set_settings_url = f'{self.base_url}set_settings/{self.settings.API_KEY}:{self.settings.SYMBOL}'
        self.set_settings()

    def load_settings(self, file):
        with open(f'{file}.json') as f:
            settings = [s for s in jsonpickle.decode(f.read())
                        if s.API_KEY == self.API_KEY]
            return settings[0]

    def get_data_for_calculations(self, orders_state):
        return {
                'active_orders': self.exchange.get_orders_state(orders_state),
                'last_prices': {'trade_price': self.exchange.get_last_trade_price(),
                                'order_price': self.exchange.get_last_order_price(self.settings.GRID_SIDE)},
                'positions': self.exchange.get_positions()
        }

    def replace_orders(self, to_create, to_cancel):
        orders_status = []
        if len(to_cancel) > 0:
            self.logger.info("Canceling %d orders:" % (len(to_cancel)))
            for order in to_cancel:
                self.logger.info(f"  {order}")
            self.exchange.cancel_all_orders()
        if len(to_create) > 0:
            self.logger.info("Creating %d orders:" % (len(to_create)))
            for order in to_create:
                responce = self.exchange.create_order(order)
                if 'order' in responce:
                    order = responce['order']
                    orders_status.append(order['order_id'])
                    self.logger.info("  %4s %d @ %.2f" % (
                        order['direction'].lower(), order['amount'], order['price']))
        return orders_status

    def set_settings(self):
        settings = {'api_key': self.settings.API_KEY,
                    'instrument': self.settings.SYMBOL,
                    'order_spread': self.settings.ORDER_SPREAD,
                    'order_step': self.settings.ORDER_STEP,
                    'start_step': self.settings.START_STEP,
                    'frequency_rate': self.settings.FREQUENCY_RATE,
                    'order_size': self.settings.ORDER_SIZE,
                    'grid_depth': self.settings.GRID_DEPTH,
                    'grid_side': self.settings.GRID_SIDE}
        result = requests.post(url=self.set_settings_url, json=settings)
        try:
            if result.status_code == 200 and result.json().get('result') == 'exchange_settings are saved':
                self.logger.info('setting the bot parameters was successful')
        except:
            raise SetSettings(
                f'setting the bot params failed'
            )

    def get_orders_for_update(self, kw):
        orders_for_update = requests.post(url=self.orders_calculator_url, json=kw)
        try:
            status_code = orders_for_update.status_code
            result = orders_for_update.json().get('result')
            if status_code == 400 and result == 'exchange_settings not found':
                self.logger.info(f'result: {result}')
                self.set_settings()
                raise SetSettings(
                    f'the exchange_settings will be available in the next iteration'
                )
            elif status_code == 200:
                return orders_for_update.json()
            else:
                raise SetSettings(
                    f'status_code: {status_code}'
                )
        except Exception as err:
            raise err

    def check_position_size(self, kw):
        active_orders = kw.get('active_orders')
        active_orders_size = sum([order.get('size') for order in active_orders
                                  if order.get('side') == self.settings.REVERSE_SIDE])
        return active_orders_size == kw.get('positions').get('size')

    async def run_loop(self):
        while True:
            try:
                kw = self.get_data_for_calculations(self.orders_state)

                if not self.check_position_size(kw):
                    await asyncio.sleep(self.settings.LOOP_INTERVAL)
                    continue

                self.logger.info(f"last_prices: {kw.get('last_prices')}")
                self.logger.info(f"positions: {kw.get('positions')}")
                self.logger.info("active_orders: ")
                for order in kw.get("active_orders"):
                    self.logger.info(f"  {order}")

                orders_for_update = self.get_orders_for_update(kw)
                for k, v in orders_for_update.items():
                    self.logger.info(f"{k}: ")
                    for order in v:
                        self.logger.info(f"  {order}")

                self.orders_state = orders_for_update.get('to_get_info') + \
                                    self.replace_orders(orders_for_update.get('to_create'),
                                                        orders_for_update.get('to_cancel'))
            except Exception as err:
                self.logger.info(f"{err}")
                await asyncio.sleep(self.settings.LOOP_INTERVAL)
                continue
            await asyncio.sleep(self.settings.LOOP_INTERVAL)

class SetSettings(Exception):
    pass