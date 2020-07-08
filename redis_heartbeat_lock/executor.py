from asyncio import wrap_future
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)


def run_sync_in_thread_pool(func, *args, **kwargs):
    """Run a synchronous function on a thread-pool, and return a future
    which yields the result of the function. """

    # executor.submit runs a sync function on a thread pool, as shown at:
    #     https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example.
    # wrap_future converts from a concurrent.futures.Future to an asyncio.Future.
    return wrap_future(executor.submit(func, *args, **kwargs))
