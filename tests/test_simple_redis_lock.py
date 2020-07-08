#!/usr/bin/env python
"""Tests for `redis-heartbeat-lock` package."""
# pylint: disable=redefined-outer-name

import pytest
import redis_heartbeat_lock


@pytest.mark.asyncio
async def test_raises_if_exception_occurs():
    """Tests that if an exception occurs during the block, we get that exception."""
    # First, build our redis client and heartbeat manager...
    redis = await redis_heartbeat_lock.AsyncRedisLock.create(
        key="test_raises_if_exception_occurs",
        lock_acquisition_timeout=2.0,
        lock_expiry=2,
    )

    heartbeat = redis_heartbeat_lock.RedisHeartbeatLock(period=1.0, redis=redis)

    with pytest.raises(
        Exception, match=r"Failed!",
    ):
        async with heartbeat as heartbeat:
            raise Exception(f"Failed!")


# Want to test...
# (1) That if an exception occurs, we catch it
# (2) If we do no work, we still shut down correctly (e.g. call exit fxn)
# (3) That I can spawn a heartbeat and have it run in the background while running other things in the foreground

# Test that if an exception occurs during heartbeat, it shuts down correctly
# Test that if we do nothing during heartbeat, it shuts down correctly
# Test that we can run things in the foreground during heartbeat
# Test that heartbeat grabs the lock as expected
# Test that heartbeat errors if the lock is already acquired by someone else
# Test that it refreshes the lock and holds it longer than initial timeout
