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

    async def wait_lock(self, wait_time: int = 10):
        """
        Wait until the model is unlocked.
        """

        while self._lock:
            logging.info("Waiting for model to unlock...")
            await asyncio.sleep(wait_time)

    def unlock(self):
        """
        Unlock the model.
        """

        self._lock = False

    def lock(self):
        """
        Lock the model
        """

        self._lock = True
