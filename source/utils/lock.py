"""
This module contains the Lock class which is used to lock.
"""

import asyncio
import logging


class Lock:
    """
    Lock class to lock and unlock the model.
    """

    def __init__(self, initial_lock_value: bool) -> None:
        self._lock = initial_lock_value
        self.time_locked = 0

    async def wait_lock(self, wait_time: int = 5, max_timeout: int = 600):
        """
        Wait until the model is unlocked.
        """

        while self._lock and self.time_locked < max_timeout:
            logging.info("Waiting for model to unlock...")
            await asyncio.sleep(wait_time)
            self.time_locked += wait_time

    async def unlock(self, wait_time: int = 1):
        """
        Unlock the model.
        """
        await asyncio.sleep(wait_time)
        self._lock = False
        self.time_locked = 0

    async def lock(self, wait_time: int = 1):
        """
        Lock the model
        """
        await asyncio.sleep(wait_time)
        self._lock = True
        self.time_locked = 0
