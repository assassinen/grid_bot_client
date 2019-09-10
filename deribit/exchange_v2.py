from models.states import OrderSide
from deribit.session import Session

class DeribitExchangeInterface:

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.instrument = instrument
        self.session = Session(key, secret, base_url, api_url)

    def get_positions(self):
        method = 'private/get_position'
        params = {'instrument_name': self.instrument}
        result = self.session.post(method, params)
        return {'average_price': result.get('average_price'),
                'size': result.get('size')}

    def get_last_trade_price(self):
        method = 'public/get_last_trades_by_instrument'
        params = {'instrument_name': self.instrument, 'count': 1}
        result = self.session.post(method, params)
        return result['trades'][0]['price'] if result else None

    def get_last_order_price(self, side):
        method = 'private/get_order_history_by_instrument'
        params = {'instrument_name': self.instrument, 'count': 1}
        last_order_price = [order['price'] for order
                            in self.session.post(method, params)
                            if order['direction'] == side]
        return last_order_price[0] if len(last_order_price) > 0 \
            else self.get_last_trade_price()

    def get_open_orders(self):
        method = 'private/get_open_orders_by_instrument'
        params = {'instrument_name': self.instrument}
        open_orders = self.session.post(method, params)
        return [{'price': order['price'],
                 'orderQty': order['amount'],
                 'side': order['direction']}
                for order in open_orders]

    def create_order(self, order):
        method = 'private/buy' if order['side'] == OrderSide.buy else 'private/sell'
        params = {
            'instrument_name': self.instrument,
            'amount': order['orderQty'],
            'price': order['price'],
            'postOnly': 'true',
            'time_in_force': 'good_til_cancelled',
            'type': 'limit'
        }
        result = self.session.post(method, params)
        return result

    def cancel_all_orders(self):
        method = 'private/cancel_all_by_instrument'
        params = {'instrument_name': self.instrument, 'type': 'all'}
        result = self.session.post(method, params)
        return result
