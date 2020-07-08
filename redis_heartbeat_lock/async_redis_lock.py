"""Simple async wrapper around a Redis client to manage getting and holding a lock."""

import asyncio
import redis
import time
from typing import Any, Optional

from .executor import run_sync_in_thread_pool


class AsyncRedisLock:
    """An async wrapper around the officially supported Redis client for Python, used to implement basic locking."""

    # The key to lock on
    key: str

    # The Redis client
    client: redis.Redis

    # Timeout when acquiring the lock
    lock_acquisition_timeout: float

    # Rate at which to check lock when acquiring it
    lock_check_rate: float

    # Expiration of the lock, in seconds
    lock_expiry: int

    def __init__(self, key: str, client: redis.Redis):
        self.key = key
        self.client = client

    @classmethod
    async def create(
        cls,
        key: str,
        host: str,
        port: int = 6379,
        db: int = 0,
        lock_acquisition_timeout: float = 8.0,
        lock_check_rate: float = 0.2,
        lock_expiry: float = 8.0,
    ) -> "AsyncRedisLock":
        """Asynchronously create a Redis client and initialize the wrapper class."""

        def _inner() -> redis.Redis:
            return redis.Redis(host, port, db)

        client = await run_sync_in_thread_pool(_inner)
        return cls(key, client)

    async def set_lock(self, value: Any, nx: bool = False) -> None:
        """Try to set the given key until we timeout."""

        def _inner():
            while (
                self.client.set(name=self.key, value=value, ex=self.lock_expiry, nx=nx)
                is not True
            ):
                time.sleep(self.lock_check_rate)

        # Timeout after our specified number of seconds
        await asyncio.wait_for(
            run_sync_in_thread_pool(_inner), timeout=self.lock_acquisition_timeout,
        )

    async def expire(self) -> None:
        """Set an expire flag on the given key."""

        def _inner():
            self.client.expire(name=self.key, time=self.lock_expiry)

        await run_sync_in_thread_pool(_inner)
