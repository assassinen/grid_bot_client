#!/usr/bin/env python
from managers.orders_manager import OrdersManager
from managers.bots_manager import BotsManager
from models.settings import Settings
import asyncio

# bots = BotsManager()
# # orders_сalculators = bots.get_orders_сalculators()
#
# loop = asyncio.get_event_loop()
#
# for orders_manager in bots.get_orders_managers():
#     loop.create_task(orders_manager.run_loop())
# loop.run_forever()

# heroku examples
from dotenv import load_dotenv
import os

load_dotenv()

settings = Settings(
    API_KEY=os.environ["API_KEY"],
    API_SECRET=os.environ["API_SECRET"],
    TOKEN=os.environ["TOKEN"],
)

loop = asyncio.get_event_loop()
orders_manager = OrdersManager(settings)
loop.create_task(orders_manager.run_loop())
loop.run_forever()