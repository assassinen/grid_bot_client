#!/usr/bin/env python
from managers.orders_manager import OrdersManager
from managers.bots_manager import BotsManager
import asyncio

bots = BotsManager()
# orders_сalculators = bots.get_orders_сalculators()

loop = asyncio.get_event_loop()

for orders_manager in bots.get_orders_managers():
    loop.create_task(orders_manager.run_loop())
loop.run_forever()
