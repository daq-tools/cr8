
from tqdm import tqdm
import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


async def execute(loop, cursor, stmt, args=None):
    f = loop.run_in_executor(None, cursor.execute, stmt, args)
    await f
    return cursor.duration


async def map_async(q, corof, iterable):
    for i in iterable:
        task = asyncio.ensure_future(corof(*i))
        await q.put(task)
    await q.put(None)


async def consume(q, total=None):
    with tqdm(total=total, unit=' requests', smoothing=0.1) as t:
        while True:
            task = await q.get()
            if task is None:
                break
            await task
            t.update(1)


async def run_sync(coro, iterable):
    for i in tqdm(iterable, unit=' requests', smoothing=0.1):
        await coro(*i)


def run(coro, iterable, concurrency, loop=None):
    loop = loop or asyncio.get_event_loop()
    if concurrency == 1:
        return loop.run_until_complete(run_sync(coro, iterable))
    q = asyncio.Queue(maxsize=concurrency)
    loop.run_until_complete(asyncio.gather(
        map_async(q, coro, iterable),
        consume(q)))
