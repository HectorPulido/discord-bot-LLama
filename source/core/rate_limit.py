"""
Rate limiting utilities for asynchronous operations.
This module provides a Throttle class to limit the rate of operations
and ensure that a minimum interval is respected between calls.
"""

import time
import asyncio


class Throttle:
    """
    A simple throttle to limit the rate of operations.
    It ensures that a minimum interval (in milliseconds) is respected between calls.
    """

    def __init__(self, min_interval_ms: int):
        self.min_interval = min_interval_ms / 1000.0
        self._last = 0.0
        self._lock = asyncio.Lock()

    async def ready(self) -> bool:
        """
        Check if the throttle is ready to allow an operation.
        Returns True if the minimum interval has passed since the last operation.
        """
        async with self._lock:
            now = time.monotonic()
            if (now - self._last) >= self.min_interval:
                self._last = now
                return True
            return False
