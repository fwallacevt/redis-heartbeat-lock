""" Shared functions and constants used throughout the package. """

DEFAULT_LOCK_ACQUISITION_TIMEOUT: float = 8.0
DEFAULT_LOCK_CHECK_RATE: float = 0.2
DEFAULT_LOCK_EXPIRY: int = 8
DEFAULT_HEARTBEAT_PERIOD: int = DEFAULT_LOCK_EXPIRY / 2
