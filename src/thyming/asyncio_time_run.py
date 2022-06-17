import asyncio
from time import perf_counter
from typing import Callable, Coroutine

from thyming.time_diff import time_diff

def asyncio_time_run(coroutine: Coroutine, logger: Callable[[str], None] = print):
    t0 = perf_counter()
    res = asyncio.run(coroutine)
    logger(f"Coroutine `{coroutine.__qualname__}` took {time_diff(t0)} seconds.")
    return res