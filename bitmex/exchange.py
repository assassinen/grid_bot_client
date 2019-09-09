from bitmex.session import Session

class ExchangeInterface:

    def __init__(self, key, secret, base_url, api_url, instrument):
        self.instrument = instrument
        self.session = Session(key, secret, base_url, api_url)

    def get_balance(self):
        result = self.session.get('user/wallet')
        return '{:.4f}'.format(result['amount'] / 10**8) if result else None

    def get_positions(self):
        query = '?filter=%7B%22symbol%22%3A%20%22{}%22%7D' \
                '&columns=%5B%22avgEntryPrice%22%5D'.format(self.instrument)
        result = self.session.get('position', query)
        positions = result[0] if result else {}
        return {'average_price': positions.get('avgEntryPrice'),
                'size': positions.get('currentQty')}

    def get_last_trade_price(self):
        query = '?symbol={}&count=1&reverse=true'.format(self.instrument)
        result = self.session.get('trade', query)
        trade_price = result[0] if result else {}
        return trade_price['price'] if result else None

    def get_last_order_price(self, side):
        last_order_price = [order['price'] for order
                            in self.get_open_orders()
                            if order['side'] == side]
        return last_order_price[0] if len(last_order_price) > 0 \
            else self.get_last_trade_price()

    def get_open_orders(self):
        query = '?filter=%7B%22ordStatus%22%3A%20%22New%22%7D&reverse=true' \
                '&columns=price%2C%20orderQty%2C%20side' \
                '&symbol={}'.format(self.instrument)

        open_orders = self.session.get('order', query)
        return [{'price': round(order['price']),
                 'orderQty': order['orderQty'],
                 'side': order['side']}
                for order in open_orders]

    def create_order(self, order=''):
        postdict = {
            'symbol': self.instrument,
            'side': order['side'],
            'orderQty': order['orderQty'],
            'price': order['price'],
            'ordType': 'Limit',
            'execInst': 'ParticipateDoNotInitiate'
        }
        return self.session.post('order', postdict)

    def cancel_all_orders(self):
        postdict = {'symbol': self.instrument}
        return self.session.delete('order/all', postdict)


