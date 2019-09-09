from models.states import OrderSide
from utils import log

class AveragePrice:

    def __init__(self, settings):
        self.API_KEY = settings.API_KEY
        self.ORDER_SPREAD = settings.ORDER_SPREAD
        self.ORDER_STEP = settings.ORDER_STEP
        self.ORDER_SIZE = settings.ORDER_SIZE
        self.GRID_DEPTH = settings.GRID_DEPTH
        self.GRID_SIDE = settings.GRID_SIDE
        self.REVERSE_SIDE = settings.REVERSE_SIDE
        self.SYMBOL = settings.SYMBOL
        self.orders = {}
        self.orders[OrderSide.sell] = {}
        self.orders[OrderSide.buy] = {}
        self.logger = log.setup_custom_logger(self.API_KEY)

    def get_api_key(self):
        return self.API_KEY

    def get_orders_price(self, orders):
        return [o['price'] for o in orders if o]

    def orders_is_converge(self):
        return sorted(self.existing_orders_price) == sorted(self.design_orders_price) \
               and self.design_orders_price != []

    def get_order_by_side(self, side):
        return [order for order in self.open_orders if order['side'] == side]

    def get_price(self, side, price=None):
        ratio = 1 if side == OrderSide.sell else -1
        delta = self.ORDER_STEP * ratio if side == self.GRID_SIDE else self.ORDER_SPREAD * ratio
        price = round(price) if price else self.last_trade_price
        return (min(price, self.last_trade_price) + delta if side == OrderSide.buy else
                max(price, self.last_trade_price) + delta)

    def over_price(self):
        side = self.GRID_SIDE
        open_order = self.get_order_by_side(side)
        return False if len(open_order) <= 0 \
            else (abs(self.get_price(side) - open_order[0]['price']) >= self.ORDER_STEP * 2)

    def create_grid_order(self):
        side = self.GRID_SIDE
        price = self.get_price(side)
        open_order = self.get_order_by_side(side)
        if len(self.orders[side]) > 0 and len(open_order) <= 0:
            last_order_price = self.last_order_price
            price = self.get_price(side, last_order_price)
        size = self.ORDER_SIZE
        order = {"price": int(price),
                 "orderQty": size,
                 "side": side}
        return order

    def update_grid_orders(self):
        if self.positions['size'] >= self.GRID_DEPTH * self.ORDER_SIZE:
            self.orders[self.GRID_SIDE] = {}
            self.logger.info("achieved the acceptable depth: {}".format(self.orders[OrderSide.buy]))
        else:
            self.orders[self.GRID_SIDE] = self.create_grid_order()
            self.logger.info("grid calculated: {}".format(self.orders[OrderSide.buy]))

    def update_reverse_orders(self):
        side = self.REVERSE_SIDE
        price = self.positions['average_price']
        size = self.positions['size']
        if size > 0:
            order = {"price": self.get_price(side, price),
                     "orderQty": size,
                     "side": side}
            self.orders[side] = order
        self.logger.info("reverse calculated: {}".format(self.orders[OrderSide.sell]))

    def unpack(self, kw):
        if len([i for i in kw.values() if i is None]) == 0:
            self.positions = kw['positions']
            self.open_orders = kw['open_orders']
            self.last_trade_price = kw['last_trade_price']
            self.last_order_price = kw['last_order_price']
            self.existing_orders_price = self.get_orders_price(self.open_orders)
            self.design_orders_price = \
                self.get_orders_price([order for order in self.orders.values()])
            return True

    def update(self, kw):
        if self.unpack(kw) and (self.over_price() or not self.orders_is_converge()):
            self.logger.info("recalculation price: {}".
                  format(not self.orders_is_converge() or self.over_price()))
            self.logger.info("existing_orders_price: {}".format(self.existing_orders_price))
            self.logger.info("design_orders_price: {}".format(self.design_orders_price))
            to_cancel = self.open_orders
            self.update_grid_orders()
            self.orders[self.REVERSE_SIDE] = {}
            self.update_reverse_orders()
            to_create = [order for order in self.orders.values() if order]
            return {'to_create': to_create, 'to_cancel': to_cancel}
        else:
            return {'to_create': [], 'to_cancel': []}

