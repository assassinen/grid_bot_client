import os, jsonpickle
from models.settings import ExchangeSettings
from models.states import OrderSide

settings = [{
    "API_KEY": "EDwDQjVbWdHgNa5V-duD1eKD",
    "API_SECRET": "T5t1bugZFKUHJLXQB3JlhHy3pD7GxfzaqanWREv4LYF6Ld_r",
    "BASE_URL": "https://testnet.bitmex.com",
    "API_URL": "/api/v1/",
    "LOOP_INTERVAL": 5
}, {
    "API_KEY": "Y3sFiwog46-1qtsxPCoK0Gpu",
    "API_SECRET": "pN9kRI_7ucOmNz6L9K79_S1meKQP2aoBxsjIpMBY-xbTSB_2",
    "BASE_URL": "https://www.bitmex.com",
    "API_URL": "/api/v1/",
    "LOOP_INTERVAL": 5
}]

testdata = [ExchangeSettings(**setting) for setting in settings]

out = 'exchange_settings.json'
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), out)

with open(file, 'w') as out:
    jsonpickle.set_encoder_options("json", indent=2)
    out.write(jsonpickle.encode(testdata))