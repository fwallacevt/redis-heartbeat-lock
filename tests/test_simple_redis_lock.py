#!/usr/bin/env python
"""Tests for `redis-heartbeat-lock` package."""
# pylint: disable=redefined-outer-name

import asyncio
import pytest
from redis_heartbeat_lock import async_lock, context_manager


@pytest.mark.asyncio
async def test_raises_if_exception_occurs():
    """Tests that if an exception occurs during the block, we get that exception."""
    # First, build our redis client and heartbeat manager...
    redis = await async_lock.AsyncLock.create(
        key="test_raises_if_exception_occurs",
        url="redis://127.0.0.1:6379",
        lock_acquisition_timeout=2.0,
        lock_expiry=2,
    )

    heartbeat = context_manager.ContextManager(period=1.0, redis=redis)

    with pytest.raises(
        Exception, match=r"Failed!",
    ):
        async with heartbeat as _:
            raise Exception(f"Failed!")

    assert heartbeat.future.done() is True
    assert heartbeat.future.cancelled() is True
    assert await redis.exists() == 0


@pytest.mark.asyncio
async def test_cleans_up_if_nothing_happens():
    """Tests that if we do nothing, the heartbeat is cleaned up."""
    # First, build our redis client and heartbeat manager...
    redis = await async_lock.AsyncLock.create(
        key="test_cleans_up_if_nothing_happens",
        url="redis://127.0.0.1:6379",
        lock_acquisition_timeout=2.0,
        lock_expiry=2,
    )

    heartbeat = context_manager.ContextManager(period=1.0, redis=redis)

    async with heartbeat as _:
        pass

    assert heartbeat.future.done() is True
    assert heartbeat.future.cancelled() is True
    assert await redis.exists() == 0


@pytest.mark.asyncio
async def test_can_run_things_in_the_foreground():
    """Tests that we can run tasks while running the heartbeat."""
    # First, build our redis client and heartbeat manager...
    redis = await async_lock.AsyncLock.create(
        key="test_can_run_things_in_the_foreground",
        url="redis://127.0.0.1:6379",
        lock_acquisition_timeout=2.0,
        lock_expiry=2,
    )

    heartbeat = context_manager.ContextManager(period=1.0, redis=redis)

    async with heartbeat as _:
        await asyncio.sleep(5)
        print("Did some stuff!")

    assert heartbeat.future.done() is True
    assert heartbeat.future.cancelled() is True
    assert await redis.exists() == 0


@pytest.mark.asyncio
async def test_gets_lock():
    """Tests that the heartbeat actually grabs the lock correctly."""
    # First, build our redis client and heartbeat manager...
    redis = await async_lock.AsyncLock.create(
        key="test_gets_lock",
        url="redis://127.0.0.1:6379",
        lock_acquisition_timeout=2.0,
        lock_expiry=4,
    )

    heartbeat = context_manager.ContextManager(period=1.0, redis=redis)

    async with heartbeat as _:
        lock = await redis.set_lock(True, True)
        assert lock == False

    assert await redis.exists() == 0


@pytest.mark.asyncio
async def test_errors_if_lock_is_acquired():
    """Tests that the heartbeat errors if someone else has the lock."""
    # First, build our redis client and heartbeat manager...
    redis = await async_lock.AsyncLock.create(
        key="test_errors_if_lock_is_acquired",
        url="redis://127.0.0.1:6379",
        lock_acquisition_timeout=2.0,
        lock_expiry=8,
    )
    lock = await redis.set_lock(True, True)
    assert lock == True

    heartbeat = context_manager.ContextManager(period=1.0, redis=redis)

    with pytest.raises(
        Exception, match=r"Failed to get lock",
    ):
        async with heartbeat as _:
            pass

    assert await redis.exists() == 1


@pytest.mark.asyncio
async def test_holds_lock():
    """Tests that the heartbeat holds the lock for longer than initial expiry."""
    # First, build our redis client and heartbeat manager...
    redis = await async_lock.AsyncLock.create(
        key="test_holds_lock",
        url="redis://127.0.0.1:6379",
        lock_acquisition_timeout=2.0,
        lock_expiry=4,
    )

    heartbeat = context_manager.ContextManager(period=2.0, redis=redis)

    async with heartbeat as _:
        lock = await redis.set_lock(True, True)
        assert lock == False

        # Should still have the lock after another five seconds
        await asyncio.sleep(5)
        lock = await redis.set_lock(True, True)
        assert lock == False

        # Should still have the lock after another five seconds
        await asyncio.sleep(5)
        lock = await redis.set_lock(True, True)
        assert lock == False

    assert await redis.exists() == 0
