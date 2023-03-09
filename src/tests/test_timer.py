import logging
# LOGGER = logging.getLogger(__name__)

import pytest

from thyming.timer import Timer, TimerAlreadyRunningError, TimerNotRunningError, DefaultMessage

def test_100ms():
    t = Timer()
    for _ in range(10):
        t.start()
        t.sleep(.1)
        t.stop()
    assert all(.1 < time < .11 for time in t.recorded_times)

class Test_exceptions:
    def test_TimerAlreadyRunningError(self):
        with pytest.raises(TimerAlreadyRunningError):
            Timer().start().start()
    def test_TimerNotRunningError(self):
        with pytest.raises(TimerNotRunningError):
            Timer().stop()
    def test_NoLoggerError(self):
        with pytest.raises(NoLoggerError):
            t = Timer(logger=None).log('test')

class Test_logger:
    ...

