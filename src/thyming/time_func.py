from functools import wraps
from time import perf_counter
from typing import Callable, TypeVar
from typing_extensions import Concatenate, ParamSpec

from thyming.time_diff import time_diff

P = ParamSpec('P')
R = TypeVar('R')
# TODO: add custom messages and loggers
def time_func(func: Callable[P, R]) -> Callable[Concatenate[bool, P], R]:
    """Time the function `func`.
    """
    @wraps(func)
    def timed(time_func=True, *args: P.args, **kwargs: P.kwargs) -> R:
        if time_func:
            t0 = perf_counter()
            res = func(*args, **kwargs)
            print(f"Function `{func.__qualname__}` took {time_diff(t0)} seconds.")
            return res
        return func(*args, **kwargs)

    return timed