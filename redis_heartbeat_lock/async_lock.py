"""Simple async wrapper around a Redis client to manage getting and holding a lock."""

import asyncio
import redis
import time
from typing import Any, Optional

from .executor import run_sync_in_thread_pool
from .shared import (
    DEFAULT_LOCK_ACQUISITION_TIMEOUT,
    DEFAULT_LOCK_CHECK_RATE,
    DEFAULT_LOCK_EXPIRY,
)


class AsyncLock:
    """An async wrapper around the officially supported Redis client for Python, used to implement basic locking."""

    # The key to lock on
    __key: str

    # The Redis client
    __client: redis.Redis

    # Timeout when acquiring the lock
    __lock_acquisition_timeout: float

    # Rate at which to check lock when acquiring it
    __lock_check_rate: float

    # Expiration of the lock, in seconds
    __lock_expiry: int

    # When we last obtained the lock
    __lock_obtained_at: float

    def __init__(
        self,
        key: str,
        client: redis.Redis,
        lock_acquisition_timeout: float,
        lock_check_rate: float,
        lock_expiry: int,
    ):
        self.__key = key
        self.__client = client
        self.__lock_acquisition_timeout = lock_acquisition_timeout
        self.__lock_check_rate = lock_check_rate
        self.__lock_expiry = lock_expiry

    @classmethod
    async def create(
        cls,
        key: str,
        url: str,
        lock_acquisition_timeout: float = DEFAULT_LOCK_ACQUISITION_TIMEOUT,
        lock_check_rate: float = DEFAULT_LOCK_CHECK_RATE,
        lock_expiry: int = DEFAULT_LOCK_EXPIRY,
    ) -> "AsyncLock":
        """Asynchronously create a Redis client and initialize the wrapper class."""

        def _inner() -> redis.Redis:
            return redis.Redis.from_url(url=url)

        client = await run_sync_in_thread_pool(_inner)
        return cls(key, client, lock_acquisition_timeout, lock_check_rate, lock_expiry)

    async def set_lock(self, value: Any, nx: bool = False) -> bool:
        """Try to set the given key until we timeout."""

        def _inner() -> bool:
            _start_time = time.time()
            _set_lock = self.__client.set(
                name=self.__key,
                value=str(value),
                ex=self.__lock_expiry,
                px=None,
                nx=nx,
            )
            while _set_lock is not True and (
                (time.time() - _start_time) < self.__lock_acquisition_timeout
            ):
                _set_lock = self.__client.set(
                    name=self.__key,
                    value=str(value),
                    ex=self.__lock_expiry,
                    px=None,
                    nx=nx,
                )
                time.sleep(self.__lock_check_rate)

            set_lock = _set_lock is True
            if set_lock is True:
                self.__lock_obtained_at = time.time()

            return set_lock

        ret = await run_sync_in_thread_pool(_inner)
        return ret

    async def set_expiration(self) -> None:
        """Set the expiration, in seconds, on the given key."""

        def _inner():
            self.__client.expire(name=self.__key, time=self.__lock_expiry)
            self.__lock_obtained_at = time.time()

        await run_sync_in_thread_pool(_inner)

    async def release(self) -> None:
        """Release the lock, if it hasn't expired."""
        if time.time() - self.__lock_obtained_at > self.__lock_expiry:
            raise Exception(f"{self.__key} lost lock before releasing.")

        def _inner():
            self.__client.delete(self.__key)

        await run_sync_in_thread_pool(_inner)

    async def exists(self) -> None:
        """Check if the key exists. Mostly for testing."""

        def _inner() -> int:
            return self.__client.exists(self.__key)

        ret = await run_sync_in_thread_pool(_inner)
        return ret
