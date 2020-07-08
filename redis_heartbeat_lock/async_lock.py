"""Simple async wrapper around a Redis client to manage getting and holding a lock."""

import asyncio
import redis
import time
from typing import Any, Optional

from .executor import run_sync_in_thread_pool


class AsyncLock:
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

    # When we last obtained the lock
    lock_obtained_at: float

    def __init__(
        self,
        key: str,
        client: redis.Redis,
        lock_acquisition_timeout: float,
        lock_check_rate: float,
        lock_expiry: int,
    ):
        self.key = key
        self.client = client
        self.lock_acquisition_timeout = lock_acquisition_timeout
        self.lock_check_rate = lock_check_rate
        self.lock_expiry = lock_expiry

    @classmethod
    async def create(
        cls,
        key: str,
        host: str = "127.0.0.1",
        port: int = 6379,
        db: int = 0,
        lock_acquisition_timeout: float = 8.0,
        lock_check_rate: float = 0.2,
        lock_expiry: int = 8,
    ) -> "AsyncLock":
        """Asynchronously create a Redis client and initialize the wrapper class."""

        def _inner() -> redis.Redis:
            return redis.Redis(host, port, db)

        client = await run_sync_in_thread_pool(_inner)
        return cls(key, client, lock_acquisition_timeout, lock_check_rate, lock_expiry)

    async def set_lock(self, value: Any, nx: bool = False) -> bool:
        """Try to set the given key until we timeout."""

        def _inner() -> bool:
            _start_time = time.time()
            _set_lock = self.client.set(
                name=self.key, value=str(value), ex=self.lock_expiry, px=None, nx=nx,
            )
            while _set_lock is not True and (
                (time.time() - _start_time) < self.lock_acquisition_timeout
            ):
                _set_lock = self.client.set(
                    name=self.key,
                    value=str(value),
                    ex=self.lock_expiry,
                    px=None,
                    nx=nx,
                )
                time.sleep(self.lock_check_rate)

            set_lock = _set_lock is True
            if set_lock is True:
                self.lock_obtained_at = time.time()

            return set_lock

        ret = await run_sync_in_thread_pool(_inner)
        return ret

    async def expire(self) -> None:
        """Set an expire flag on the given key."""

        def _inner():
            self.client.expire(name=self.key, time=self.lock_expiry)
            self.lock_obtained_at = time.time()

        await run_sync_in_thread_pool(_inner)

    async def release(self) -> None:
        """Release the lock, if it hasn't expired."""
        if time.time() - self.lock_obtained_at > self.lock_expiry:
            raise Exception(f"{self.key} lost lock before releasing.")

        def _inner():
            self.client.delete(self.key)

        await run_sync_in_thread_pool(_inner)

    async def exists(self) -> None:
        """Check if the key exists. Mostly for testing."""

        def _inner() -> int:
            return self.client.exists(self.key)

        ret = await run_sync_in_thread_pool(_inner)
        return ret
