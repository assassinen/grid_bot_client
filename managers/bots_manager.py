import jsonpickle
from strategy.average_price import AveragePrice

class BotsManager():

    def __init__(self):
        self.file_settings = 'settings/grid_settings'
        self.strategies = {
            'average_price': AveragePrice
        }
        self.orders_сalculators = self.create_orders_сalculator()

    def load_settings(self, file=None):
        testdata_file = f'{file}.json' if file else f'{self.file_settings}.json'
        with open(testdata_file) as f:
            return jsonpickle.decode(f.read())

    def create_orders_сalculator(self):
        return [self.strategies[setting.strategy](setting)
                for setting in self.load_settings() if setting.active]

    def get_orders_сalculator_by_key(self, api_key):
        return self.orders_сalculators.get(api_key)

    def get_orders_сalculators(self):
        return self.orders_сalculators
