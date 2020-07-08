"""Main module. Builds on top of our redis client, adding a heartbeat and context manager."""

import asyncio

from .async_lock import AsyncLock


class ContextManager:
    """Manages starting and stopping heartbeat polling on a particular endpoint"""

    # Period to poll the heartbeat on
    __period: float

    # The heartbeat task
    __future: asyncio.Task

    # Redis lock
    __redis: AsyncLock

    def __init__(self, period: float, redis: AsyncLock):
        self.__period = period
        self.__redis = redis

    async def __heartbeat(self) -> None:
        """Refresh the Redis lock and go back to sleep."""
        while True:
            await self.__redis.set_expiration()
            await asyncio.sleep(self.__period)

    async def __aenter__(self) -> None:
        """Start the heartbeat. First, we set the Redis lock, then start the background task."""
        lock = await self.__redis.set_lock(value=True, nx=True)
        if lock is not True:
            raise Exception(f"Failed to get lock.")

        self.future = asyncio.create_task(self.__heartbeat())

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Stop the heartbeat task. We have to cancel the future, since it's on an infinite loop,
        and then wait for it to finish."""
        # First, stop the heartbeat
        self.future.cancel()
        try:
            await self.future
        except asyncio.CancelledError:
            pass

        # We don't have to worry about closing Redis - the Redis library manages that for us. However,
        # we do need to release the lock.
        await self.__redis.release()
