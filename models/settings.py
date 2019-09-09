from models.states import OrderSide

class GridSettings:

    def __init__(self,
                 API_KEY,
                 ORDER_SPREAD,
                 ORDER_STEP,
                 ORDER_SIZE,
                 GRID_DEPTH,
                 GRID_SIDE,
                 SYMBOL,
                 strategy='average_price',
                 active=True
                 ):
        self.API_KEY = API_KEY
        self.ORDER_SPREAD = ORDER_SPREAD
        self.ORDER_STEP = ORDER_STEP
        self.ORDER_SIZE = ORDER_SIZE
        self.GRID_DEPTH = GRID_DEPTH
        self.GRID_SIDE = GRID_SIDE
        self.REVERSE_SIDE = OrderSide.sell if GRID_SIDE == OrderSide.buy else OrderSide.buy
        self.RATIO = 1 if self.REVERSE_SIDE == OrderSide.sell else -1
        self.SYMBOL = SYMBOL
        self.strategy = strategy
        self.active = active

class ExchangeSettings:

    def __init__(self,
                 API_KEY,
                 API_SECRET,
                 BASE_URL,
                 API_URL,
                 LOOP_INTERVAL,
                 EXCHANGE
                 ):
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.BASE_URL = BASE_URL
        self.API_URL = API_URL
        self.LOOP_INTERVAL = LOOP_INTERVAL
        self.EXCHANGE = EXCHANGE