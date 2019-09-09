from bitmex.exchange import ExchangeInterface
import jsonpickle
import asyncio



class OrdersManager:

    def __init__(self, orders_сalculator):
        self.file_settings = 'settings/exchange_settings'
        self.orders_сalculator = orders_сalculator
        self.API_KEY = self.orders_сalculator.API_KEY
        self.GRID_SIDE = self.orders_сalculator.GRID_SIDE
        self.settings = self.load_settings()
        self.LOOP_INTERVAL = self.settings.LOOP_INTERVAL
        self.exchange = ExchangeInterface(key=self.settings.API_KEY,
                                          secret=self.settings.API_SECRET,
                                          base_url=self.settings.BASE_URL,
                                          api_url=self.settings.API_URL,
                                          instrument=self.orders_сalculator.SYMBOL)

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
            'positions': self.get_positions(),
            'open_orders': self.get_open_orders(),
            'last_trade_price': self.get_last_trade_price(),
            'last_order_price': self.get_last_order_price()
        }

    async def run_loop(self):
        while True:
            try:
                kw = self.get_data_for_orders_сalculator()
                orders_for_update = self.orders_сalculator.update(kw)
                self.replace_orders(orders_for_update['to_create'],
                                    orders_for_update['to_cancel'])
            except Exception as r:
                print(r)
            await asyncio.sleep(self.LOOP_INTERVAL)


    def replace_orders(self, to_create, to_cancel):
        # print("Orders for create: {}".format(to_create))
        # print("Orders for cancel: {}".format(to_cancel))

        # Could happen if we exceed a delta limit
        if len(to_cancel) > 0:
            print("Canceling %d orders:" % (len(to_cancel)))
            for order in to_cancel:
                print("%4s %d @ %d" % (
                order['side'], order['orderQty'], order['price']))
            self.exchange.cancel_all_orders()

        if len(to_create) > 0:
            print("Creating %d orders:" % (len(to_create)))
            for order in to_create:
                responce = self.exchange.create_order(order)
                if 'orderID' in responce:
                    print("%4s %d @ %d" % (
                    responce['side'], responce['orderQty'], responce['price']))