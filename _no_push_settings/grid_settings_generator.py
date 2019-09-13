import os, jsonpickle
from log.settings import GridSettings
from log.states import OrderSide

settings = [{
    "API_KEY": "Y3sFiwog46-1qtsxPCoK0Gpu",
    "ORDER_SPREAD": 10,
    "ORDER_STEP": 30,
    "ORDER_SIZE": 50,
    "GRID_DEPTH": 5,
    "GRID_SIDE": OrderSide.buy,
    "SYMBOL": "XBTUSD"
}, {
    "API_KEY": "EDwDQjVbWdHgNa5V-duD1eKD",
    "ORDER_SPREAD": 10,
    "ORDER_STEP": 30,
    "ORDER_SIZE": 50,
    "GRID_DEPTH": 10,
    "GRID_SIDE": OrderSide.buy,
    "SYMBOL": "XBTUSD"
}]

testdata = [GridSettings(**setting) for setting in settings]

out = 'grid_settings.json'
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), out)

with open(file, 'w') as out:
    jsonpickle.set_encoder_options("json", indent=2)
    out.write(jsonpickle.encode(testdata))