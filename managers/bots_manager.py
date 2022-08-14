from managers.orders_manager import OrdersManager
from dotenv import load_dotenv
from models.settings import Settings
import os
import json

load_dotenv()


class BotsManager():

    def __init__(self):
        self.default_settings = {
            'DERIBIT': {
                'BASE_URL': 'https://www.deribit.com/',
                'API_URL': 'api/v2/',
                'LOOP_INTERVAL': 10,
                'INSTRUMENT': 'BTC-PERPETUAL',
                'STRATEGY': 'trades_price'
            },
            'BITFINEX': {
                'BASE_URL': 'https://api.bitfinex.com/',
                'API_URL': 'v2',
                'LOOP_INTERVAL': 10,
                'INSTRUMENT': 'tBTCUSD',
                'STRATEGY': 'trades_price'
            }
        }
        self.orders_managers = self.create_orders_manager_from_env()


    def get_orders_managers(self):
        return self.orders_managers

    def get_settings(self, exchange):
        default_settings = self.default_settings.get(exchange, {})
        settings = Settings(
            API_KEY=os.getenv(f'{exchange}_API_KEY'),
            API_SECRET=os.getenv(f'{exchange}_API_SECRET'),
            TOKEN=os.getenv(f'{exchange}_API_TOKEN'),
            BASE_URL=os.getenv(f'{exchange}_BASE_URL', default_settings.get('BASE_URL')),
            API_URL=os.getenv(f'{exchange}_API_URL', default_settings.get('API_URL')),
            LOOP_INTERVAL=os.getenv(f'{exchange}_LOOP_INTERVAL', default_settings.get('LOOP_INTERVAL')),
            EXCHANGE=os.getenv(f'{exchange}_EXCHANGE', exchange.lower()),
            INSTRUMENT=os.getenv(f'{exchange}_INSTRUMENT', default_settings.get('INSTRUMENT')),
        )
        return settings

    def create_orders_manager_from_env(self):
        exchanges = self.default_settings.keys()
        return [OrdersManager(self.get_settings(exchange)) for exchange in exchanges
                if self.get_settings(exchange).is_correct_settings()]
