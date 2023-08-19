"""
Util to run sync functions in a thread pool.
"""

import functools
import typing
import asyncio


def to_thread(func: typing.Callable) -> typing.Coroutine:
    """
    Function to run sync functions in a thread pool.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
