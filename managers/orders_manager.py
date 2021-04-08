import asyncio
import requests
import jsonpickle
from bitmex.exchange import BitmexExchangeInterface
from deribit.exchange_v2 import DeribitExchangeInterface
from models.log import setup_custom_logger


class OrdersManager:

    def __init__(self, grid_settings):
        self.file_settings = 'settings/exchange_settings'
        self.grid_settings = grid_settings
        self.API_KEY = grid_settings.API_KEY
        self.GRID_SIDE = grid_settings.GRID_SIDE

        self.settings = self.load_settings()
        self.LOOP_INTERVAL = self.settings.LOOP_INTERVAL
        self.exchanges = {
            'bitmex': BitmexExchangeInterface,
            'deribit': DeribitExchangeInterface
        }
        self.exchange = self.exchanges[self.settings.EXCHANGE](key=self.settings.API_KEY,
                                                               secret=self.settings.API_SECRET,
                                                               base_url=self.settings.BASE_URL,
                                                               api_url=self.settings.API_URL,
                                                               instrument=self.grid_settings.SYMBOL)
        self.logger = setup_custom_logger(f'orders_manager.{self.settings.API_KEY}')
        self.orders_state = []
        self.base_url = 'http://moneyprinter.pythonanywhere.com/api/v1.0/'
        self.orders_calculator_url = f'{self.base_url}orders_calculator/{self.API_KEY}:{self.grid_settings.SYMBOL}'
        self.settings_url = f'{self.base_url}set_settings/{self.API_KEY}:{self.grid_settings.SYMBOL}'


    def load_settings(self, file=None):
        testdata_file = f'{file}.json' if file else f'{self.file_settings}.json'
        with open(testdata_file) as f:
            settings = [s for s in jsonpickle.decode(f.read())
                        if s.API_KEY == self.API_KEY]
            return settings[0]


    def get_data_for_calculations(self, orders_state):
        return {'last_prices': {'trade_price': self.exchange.get_last_trade_price(),
                                'order_price': self.exchange.get_last_order_price(self.GRID_SIDE)},
                'positions': self.exchange.get_positions(),
                'active_orders': self.exchange.get_orders_state(orders_state)}

    def replace_orders(self, to_create, to_cancel):
        orders_status = []
        if len(to_cancel) > 0:
            self.logger.info("Canceling %d orders:" % (len(to_cancel)))
            for order in to_cancel:
                self.logger.info(f"{order}")
                # logger.info(f"{order['side']}, {order['size']}, {order['price']}")
            self.exchange.cancel_all_orders()
        if len(to_create) > 0:
            self.logger.info("Creating %d orders:" % (len(to_create)))
            for order in to_create:
                responce = self.exchange.create_order(order)
                if 'order' in responce:
                    order = responce['order']
                    orders_status.append(order['order_id'])
                    self.logger.info("%4s %d @ %.2f" % (
                        order['direction'].lower(), order['amount'], order['price']))
        return orders_status

    def set_settings(self):
        settings = {'api_key': self.grid_settings.API_KEY,
                    'instrument': self.grid_settings.SYMBOL,
                    'order_spread': self.grid_settings.ORDER_SPREAD,
                    'order_step': self.grid_settings.ORDER_STEP,
                    'start_step': self.grid_settings.START_STEP,
                    'frequency_rate': self.grid_settings.FREQUENCY_RATE,
                    'order_size': self.grid_settings.ORDER_SIZE,
                    'grid_depth': self.grid_settings.GRID_DEPTH,
                    'grid_side': self.grid_settings.GRID_SIDE}
        result = requests.post(url=self.settings_url, json=settings)
        try:
            if result.status_code == 200 and result.json().get('result') == 'settings are saved':
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
            if status_code == 400 and result == 'settings not found':
                self.logger.info(f'result: {result}')
                self.set_settings()
                raise SetSettings(
                    f'the settings will be available in the next iteration'
                )
            else:
                return orders_for_update.json()
        except Exception as err:
            raise err



    async def run_loop(self):
        while True:
            kw = self.get_data_for_calculations(self.orders_state)
            print(kw)

            self.logger.info(f"last_prices: {kw.get('last_prices')}")
            self.logger.info(f"positions: {kw.get('positions')}")
            self.logger.info(f"active_orders: ")

            try:
                orders_for_update = self.get_orders_for_update(kw)
                print(orders_for_update)
            except Exception as err:
                self.logger.info(f"{err}")
                await asyncio.sleep(self.LOOP_INTERVAL)
                continue
            await asyncio.sleep(self.LOOP_INTERVAL)


class SetSettings(Exception):
    pass