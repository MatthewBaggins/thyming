from time import perf_counter
from typing import Union

def time_diff(t0: float, t1: Union[float, None] = None, precision: int = 2) -> float:
    """Compute time difference of two times in seconds with 1/100 sec precision.

    Args
    ----------
    t0 : float
        Earlier time.
    t1 : float | None, default=None
        Later time.

    Returns
    ----------
    float
        Time difference (t1 - t0) in seconds with 1/100 sec precision.
    """
    if not t1:
        t1 = perf_counter()
    
    return round(t1 - t0, precision)
