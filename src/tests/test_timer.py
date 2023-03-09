#pylint:disable=invalid-name,missing-function-docstring
from time import sleep

import pytest

from thyming.timer import (
    Timer,
    TimerAlreadyRunningError,
    TimerNotRunningError,
)


def test_100ms():
    """Test if Timer correctly measures time on 100 ms intervals"""
    t = Timer()
    for _ in range(10):
        t.start()
        sleep(0.1)
        t.stop()
    assert all(0.1 < time < 0.11 for time in t.times)

class Test_context_manager:
    """Test if Timer works properly as context manager"""
    
    def test_context_manager_1(self):
        with Timer() as t:
            sleep(1)
            t.measure()
            sleep(1)
            t.measure()
            sleep(1)
        assert all(1 < tdiff < 1.02 for tdiff in t.diffs())


    def test_context_manager_2(self):
        """Test if context manager works properly"""
        with Timer() as t:
            sleep(1)
            t.measure()
            sleep(1)
            t.measure()
            sleep(1)
        assert sum(t.diffs()) == t.times[-1]
class Test_exceptions:
    def test_TimerAlreadyRunningError(self):
        with pytest.raises(TimerAlreadyRunningError):
            Timer().start().start()

    def test_TimerNotRunningError(self):
        with pytest.raises(TimerNotRunningError):
            Timer().stop()

