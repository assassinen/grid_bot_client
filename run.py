from managers.bots_manager import BotsManager
import asyncio


bots = BotsManager()

loop = asyncio.get_event_loop()

for orders_manager in bots.get_orders_managers():
    loop.create_task(orders_manager.run_loop())
loop.run_forever()


# bots = BotsManager()
#
# async def main_loop(loop):
#     tasks = []
#     while True:
#         for orders_manager in bots.get_all_orders_managers():
#             print(id(orders_manager))
#             if orders_manager.active and orders_manager.name not in [task.get_name() for task in tasks]:
#                 task = loop.create_task(orders_manager.run_loop(), name=orders_manager.name)
#                 tasks.append(task)
#             elif not orders_manager.active:
#                 [task.cancel() for task in tasks if task.get_name() == orders_manager.name]
#                 tasks = [task for task in tasks if task.get_name() != orders_manager.name]
#         await asyncio.sleep(3)
#
#
# loop = asyncio.get_event_loop()
# loop.create_task(main_loop(loop))
# loop.run_forever()
