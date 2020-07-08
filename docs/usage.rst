=====
Usage
=====

To use Redis heartbeat lock in a project::

    from redis_heartbeat_lock import async_context, context_manager

    # Initialize Redis client.
    redis = await async_context.AsyncLock.create(
        key="my_key",
        host="my_host", # default 127.0.0.1
        port=1234, # default 6379
        db=0, # default 0
        lock_acquisition_timeout=2.0, # default 8.0
        lock_check_rate=0.2, # default 0.2
        lock_expiry=8, # default 8
    )

    # Use the context manager to hold a lock while doing work, refreshing every `period` seconds
    async with context_manager.ContextManager(period=1.0, redis=redis) as _:
        try:
            # Do some stuff
            raise Exception("Something failed")
        except Exception as e:
            # Handle any errors. This includes logging, saving, raising the error up, etc.
            print(f"My task failed with {str(e)})
            raise e
