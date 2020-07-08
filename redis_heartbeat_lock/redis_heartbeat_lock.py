"""Main module. Builds on top of our redis client, adding a heartbeat and context manager."""

import asyncio

from .async_redis_lock import AsyncRedisLock


class RedisHeartbeatLock:
    """Manages starting and stopping heartbeat polling on a particular endpoint"""

    # Period to poll the heartbeat on
    period: float

    # The heartbeat task
    future: asyncio.Task

    # Redis client
    redis: AsyncRedisLock

    def __init__(self, period: float, redis: AsyncRedisLock):
        self.period = period
        self.redis = redis

    async def heartbeat(self) -> None:
        """Refresh the Redis lock and go back to sleep."""
        while True:
            await self.redis.expire()
            await asyncio.sleep(self.period)

    async def __aenter__(self) -> None:
        """Start the heartbeat. First, we set the Redis lock, then start the background task."""
        lock = await self.redis.set_lock(value=True, nx=True)
        if lock is not True:
            raise Exception(f"Failed to get lock.")

        self.future = asyncio.create_task(self.heartbeat())

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
        await self.redis.release()
