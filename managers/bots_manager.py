import jsonpickle
from managers.orders_manager import OrdersManager

class BotsManager():

    def __init__(self):
        self.file_settings = 'settings/grid_settings'
        self.orders_managers = self.create_orders_manager()

    def load_settings(self, file=None):
        testdata_file = f'{file}.json' if file else f'{self.file_settings}.json'
        with open(testdata_file) as f:
            return jsonpickle.decode(f.read())

    def create_orders_manager(self):
        return [OrdersManager(setting) for setting in self.load_settings() if setting.active]

    def get_orders_managers(self):
        return self.orders_managers
