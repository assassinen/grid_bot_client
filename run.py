#!/usr/bin/env python
from managers.orders_manager import OrdersManager
from managers.bots_manager import BotsManager
import asyncio
import time

# bots = BotsManager()
# orders_сalculators = bots.get_orders_сalculators()

class OrdersManager:

    def __init__(self, message, sleep):
        self.message = message
        self.sleep = sleep

    async def run_loop(self):
        while True:
            await asyncio.sleep(self.sleep)
            print(self.message, time.strftime('%X'))

class TestBostManager:

    def __init__(self):
        self.orders_managers = self.create_orders_manager()

    def create_orders_manager(self):
        return [OrdersManager('hello', 1),  OrdersManager('world', 2)]

    def get_orders_managers(self):
        return self.orders_managers

bots = TestBostManager()

loop = asyncio.get_event_loop()

# for orders_manager in bots.get_orders_managers():
#     loop.create_task(orders_manager.run_loop())
# loop.run_forever()


# async def run_loop():
#     while True:
#         await asyncio.sleep(3)
#         print('self.message', time.strftime('%X'))
#
# import asyncio
# import time
#
async def say_after(what, delay):
    while True:
        await asyncio.sleep(delay)
        print(what, time.strftime('%X'))
    # return 123

# import asyncio
# loop=asyncio.get_event_loop()
# loop.run_forever(
#     asyncio.gather(
#         say_after('hello', 1),
#         say_after('world', 2),
#     )
# )
from asyncio import gather, get_event_loop, sleep

class ErrorThatShouldCancelOtherTasks(Exception):
    pass

# async def main():
#     tasks = [asyncio.ensure_future(say_after(f'what_{secs}', secs))
#              for secs in [2, 5, 7]]
#     try:
#         await asyncio.gather(*tasks)
#     except ErrorThatShouldCancelOtherTasks:
#         print('Fatal error; cancelling')
#         for t in tasks:
#             t.cancel()
#     finally:
#         await sleep(5)

# async def main():
#     await asyncio.sleep(1)
#     print('hello')

# asyncio.run(main())


# import asyncio
# loop = asyncio.get_event_loop()
# loop.create_task(say_after('hello', 1))
# loop.create_task(say_after('world', 2))
# print(dir(loop))
# loop.run_forever()


# loop = asyncio.get_event_loop()
#
# # for orders_manager in bots.get_orders_managers():
# loop.create_task(say_after('123', 3))
# loop.run_forever()

import asyncio

async def task_func():
    print('in task_func', time.strftime('%X'))
    # if the task needs to run for a while you'll need an await statement
    # to provide a pause point so that other coroutines can run in the mean time
    # await some_db_or_long_running_background_coroutine()
    await asyncio.sleep(1)
    # or if this is a once-off thing, then return the result,
    # but then you don't really need a Task wrapper...
    # return 'the result'

async def say_after(what, delay):
    for i in range(delay * delay):
        await asyncio.sleep(delay)
        print(what, time.strftime('%X'))
    # while True:
    #     await asyncio.sleep(delay)
    #     print(what, time.strftime('%X'))

async def my_app(what, delay):
    # my_task = asyncio.ensure_future(say_after(what, delay))
    # print(f'my_task: {my_task}')
    # if not my_task.cancelled():
    #     my_task.cancel()
    # else:
    #     my_task = None

    my_task = None

    if my_task is None:
        my_task = asyncio.ensure_future(say_after(what, delay))

    elif my_task:
        print(f'my_task: my_task')
        if not my_task.cancelled():
            my_task.cancel()
        # else:
        #     my_task = None

asyncio.ensure_future(say_after('123', 2))
asyncio.ensure_future(say_after('321', 1))

event_loop = asyncio.get_event_loop()
event_loop.run_forever()
