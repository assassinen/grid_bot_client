from models.states import OrderSide


class Settings:

    def __init__(self,
                 API_KEY,
                 API_SECRET,
                 TOKEN,
                 BASE_URL,
                 API_URL,
                 LOOP_INTERVAL,
                 EXCHANGE,
                 ORDER_SPREAD,
                 ORDER_STEP,
                 START_STEP,
                 FREQUENCY_RATE,
                 ORDER_SIZE,
                 GRID_DEPTH,
                 GRID_SIDE,
                 SYMBOL,
                 strategy='average_price',
                 active=False
                 ):
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.TOKEN = TOKEN
        self.BASE_URL = BASE_URL
        self.API_URL = API_URL
        self.LOOP_INTERVAL = LOOP_INTERVAL
        self.EXCHANGE = EXCHANGE
        self.ORDER_SPREAD = ORDER_SPREAD
        self.ORDER_STEP = ORDER_STEP
        self.START_STEP = START_STEP
        self.FREQUENCY_RATE = FREQUENCY_RATE
        self.ORDER_SIZE = ORDER_SIZE
        self.GRID_DEPTH = GRID_DEPTH
        self.GRID_SIDE = GRID_SIDE
        self.REVERSE_SIDE = OrderSide.sell if GRID_SIDE == OrderSide.buy else OrderSide.buy
        self.RATIO = 1 if self.REVERSE_SIDE == OrderSide.sell else -1
        self.SYMBOL = SYMBOL
        self.strategy = strategy
        self.active = active
