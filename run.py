#!/usr/bin/env python
import asyncio

from managers.bots_manager import BotsManager


bots = BotsManager()
loop = asyncio.get_event_loop()

for orders_manager in bots.get_orders_managers():
    loop.create_task(orders_manager.run_loop())
loop.run_forever()
