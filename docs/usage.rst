=====
Usage
=====

To use Redis heartbeat lock in a project::

    import redis_heartbeat_lock

    # Initialize Redis client.
    redis = await redis_heartbeat_lock.AsyncLock.create(
        key="my_key",
        host="my_host", # default 127.0.0.1
        port=1234, # default 6379
        db=0, # default 0
        lock_acquisition_timeout=2.0, # default 8.0
        lock_check_rate=0.2, # default 0.2
        lock_expiry=8, # default 8
    )

    # Use the context manager to hold a lock while doing work, refreshing every `period` seconds
    async with redis_heartbeat_lock.ContextManager(period=1.0, redis=redis) as _:
        # Do some stuff
        pass
