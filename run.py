#!/usr/bin/env python
from managers.orders_manager import OrdersManager
from managers.bots_manager import BotsManager
import asyncio

bots = BotsManager()
orders_managers = [OrdersManager(сalc) for сalc in bots.get_orders_сalculators()]

loop = asyncio.get_event_loop()

for order_manager in orders_managers:
    loop.create_task(order_manager.run_loop())
loop.run_forever()

