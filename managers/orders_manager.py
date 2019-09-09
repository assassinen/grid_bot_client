from bitmex.exchange import BitmexExchangeInterface
from deribit.exchange_v2 import DeribitExchangeInterface
import jsonpickle
import asyncio
import logging


class OrdersManager:

    def __init__(self, orders_сalculator):
        self.file_settings = 'settings/exchange_settings'
        self.orders_сalculator = orders_сalculator
        self.API_KEY = self.orders_сalculator.API_KEY
        self.GRID_SIDE = self.orders_сalculator.GRID_SIDE
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
                                                               instrument=self.orders_сalculator.SYMBOL)
        self.logger = logging.getLogger(f'orders_manager.{self.API_KEY}')
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=log_format, level=logging.INFO)
        
        
    def load_settings(self, file=None):
        testdata_file = f'{file}.json' if file else f'{self.file_settings}.json'
        with open(testdata_file) as f:
            settings = [s for s in jsonpickle.decode(f.read())
                        if s.API_KEY == self.API_KEY]
            return settings[0]

    def get_positions(self):
        return self.exchange.get_positions()

    def get_open_orders(self):
        return self.exchange.get_open_orders()

    def get_last_trade_price(self):
        return self.exchange.get_last_trade_price()

    def get_last_order_price(self):
        return self.exchange.get_last_order_price(self.GRID_SIDE)

    def get_data_for_orders_сalculator(self):
        return {
            'last_trade_price': self.get_last_trade_price(),
            'last_order_price': self.get_last_order_price(),
            'open_orders': self.get_open_orders(),
            'positions': self.get_positions()
        }

    async def run_loop(self):
        while True:
            try:
                kw = self.get_data_for_orders_сalculator()
                orders_for_update = self.orders_сalculator.update(kw)
                self.replace_orders(orders_for_update['to_create'],
                                    orders_for_update['to_cancel'])
            except Exception as r:
                self.logger.info(self.API_KEY)
                self.logger.info(r)
            await asyncio.sleep(self.LOOP_INTERVAL)


    def is_not_correct(self, to_create):
        reverse_orders_qty = sum([order['orderQty'] for order in to_create
                                  if order['side'] != self.GRID_SIDE])
        positions_qty = self.get_positions()['size']

        return reverse_orders_qty > positions_qty


    def replace_orders(self, to_create, to_cancel):
        if len(to_cancel) > 0:
            self.logger.info("Canceling %d orders:" % (len(to_cancel)))
            for order in to_cancel:
                self.logger.info("%4s %d @ %d" % (
                order['side'], order['orderQty'], order['price']))
            self.exchange.cancel_all_orders()

        if self.is_not_correct(to_create):
            return

        if len(to_create) > 0:
            self.logger.info("Creating %d orders:" % (len(to_create)))
            for order in to_create:
                responce = self.exchange.create_order(order)
                if 'orderID' in responce:
                    self.logger.info("%4s %d @ %d" % (
                        responce['side'], responce['orderQty'], responce['price']))
                if 'order' in responce:
                    order = responce['order']
                    self.logger.info("%4s %d @ %d" % (
                        order['direction'], order['amount'], order['price']))
