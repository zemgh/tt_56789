from functools import wraps
from typing import Coroutine, Callable


def errors_handler(func: Callable[..., Coroutine]) -> Callable[..., Coroutine] | None:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # log
            pass

    return wrapper
