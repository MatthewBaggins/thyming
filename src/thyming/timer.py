from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime as dt
from enum import Enum
import logging
from time import perf_counter
from types import TracebackType
from typing import Callable, Literal, Optional, Union
from typing_extensions import Self

###############
#    Types    #
###############

Action = Literal["measure", "stop"]
"""Two types of action"""


class DefaultMessage(Enum):
    """3 types of default message printed by `Timer` in appropriate contexts:
    when it starts, when it measures time, and when it stops
    """

    START = 0
    MEASURE = 1
    END = 2


START = DefaultMessage.START
MEASURE = DefaultMessage.MEASURE
END = DefaultMessage.END

TimerMessage = Union[str, None, DefaultMessage]
"""Instructions that can be passed to `Timer` to log a message.
- `str` - log that string verbatim
- `None` - don't log anything
- `DefaultMessage` - log default formatted message appropriate for that context
"""


###############
#    Timer    #
###############


@dataclass
class Timer:
    """Custom Timer that can be used many times to log and store times.
    It can be also used as a context manager.
    """

    name: Optional[str] = None
    """Name given to the timer"""

    message: str = "Elapsed time: {:0.4f} seconds."
    """Message printed by the timer upon clicking"""

    logger: Optional[Callable[[str], None]] = field(default=logging.info)
    """Logger used to log message upon starting, measuring, or stopping"""

    start_time: Optional[float] = field(default=None, repr=False)
    """Starting time, from which time is currently being counted"""

    times: list[float] = field(default_factory=list, init=False, repr=False)
    """List of recorded times"""

    prev_times: list[list[float]] = field(default_factory=list, init=False, repr=False)
    """Previous recorded times. `times` are moved here on subsequent timer starts."""

    def start(self, click_message: TimerMessage = None) -> Self:
        """Start measuring time"""
        if self.times:
            self.prev_times.append(self.times)
            self.times = []
        if self.start_time is not None:
            raise TimerAlreadyRunningError(self._timer_name, dt.now())
        self.start_time = perf_counter()
        if click_message:
            if self.logger is not None:
                self.log(click_message)
        return self

    def stop(
        self,
        msg_pre: TimerMessage = None,
        msg_post: TimerMessage = None,
    ) -> float:
        """Stop timer, return recorded time (since last start) in seconds"""
        return self._click(
            stop_timer=True,
            msg_pre=msg_pre,
            msg_post=msg_post,
            action="stop",
        )

    def measure(
        self,
        msg_pre: TimerMessage = None,
        msg_post: TimerMessage = None,
    ) -> float:
        """Measure time at this moment, return recorded time (since last start) in seconds"""
        return self._click(
            stop_timer=False,
            msg_pre=msg_pre,
            msg_post=msg_post,
            action="measure",
        )

    def log(self, msg: TimerMessage) -> Timer:
        """Log the message"""
        if self.logger is None:
            return self
        if msg is None:
            return self
        if isinstance(msg, DefaultMessage):
            self.logger(Timer._timestamp_to_msg(msg))
            return self
        for msg_line in msg.split("\n"):
            self.logger(msg_line)
        return self

    def restart(self, msg_pre: TimerMessage, msg_post: TimerMessage) -> Timer:
        """Restart the timer, i.e. stop it and start immediately"""
        self.stop(msg_pre, msg_post)
        return self.start()

    def rtimes(self, digits: int = 4) -> list[float]:
        """Rounded recorded times"""
        return [round(t, digits) for t in self.times]

    #################
    #    Private    #
    #################

    @staticmethod
    def _timestamp_to_msg(timestamp: DefaultMessage) -> str:
        """Convert timestamp to log message"""
        if timestamp == DefaultMessage.START:
            return f"START: {dt.now().isoformat('T', 'seconds')}"
        if timestamp == DefaultMessage.MEASURE:
            return f"MEASURED: {dt.now().isoformat('T', 'seconds')}"
        # timestamp == Timestamp.END:
        return f"END: {dt.now().isoformat('T', 'seconds')}"

    @property
    def _timer_name(self) -> str:
        if self.name:
            return f"Timer {self.name}"
        return "Timer <Unnamed>"

    def _get_logging_message(
        self,
        *,
        recorded_time: float,
        msg_pre: TimerMessage,
        msg_post: TimerMessage,
    ) -> str:
        if isinstance(msg_pre, DefaultMessage):
            msg_pre = Timer._timestamp_to_msg(msg_pre)
        if isinstance(msg_post, DefaultMessage):
            msg_post = Timer._timestamp_to_msg(msg_post)
        if msg_pre:
            msg = f"{msg_pre}\n"
        elif self.name:
            msg = f"{self.name}:\n"
        else:
            msg = ""
        msg += self.message.format(recorded_time)
        if msg_post:
            msg += "\n" + msg_post
        return msg

    def _click(
        self,
        *,
        stop_timer: bool,
        msg_pre: TimerMessage,
        msg_post: TimerMessage,
        action: Action,
    ) -> float:
        """Store current time in `self.recorded_times`
        and start counting again unless `stop_timer=True`.
        `click_message_pre` and `click_message_post` specify what message (if any)
        should be logged before and after stopping.
        """
        if self.start_time is None:
            raise TimerNotRunningError(self._timer_name, dt.now(), action)
        recorded_time = perf_counter() - self.start_time
        if stop_timer:
            self.start_time = None
        self.times.append(recorded_time)
        if self.logger:
            self.log(
                self._get_logging_message(
                    recorded_time=recorded_time,
                    msg_pre=msg_pre,
                    msg_post=msg_post,
                )
            )
        return recorded_time

    ###############
    #    Magic    #
    ###############

    def __enter__(self) -> Self:
        return self.start()

    def __exit__(
        self,
        __exc_type: Optional[type[BaseException]],
        __exc_val: Optional[BaseException],
        __exc_tb: Optional[TracebackType],
    ) -> None:
        if self.start_time is not None:
            self.stop()


################
#    Errors    #
################


@dataclass
class AbstractTimerError(Exception, ABC):
    """Abstract error raised by `Timer`"""

    timer_name: str
    timestamp: dt
    message: str = field(init=False)

    @abstractmethod
    def __post_init__(self) -> None:
        ...


@dataclass
class TimerAlreadyRunningError(AbstractTimerError):
    """Error raised when one tries to start a timer that's already running"""

    def __post_init__(self) -> None:
        self.message = (
            f"[{self.timestamp.isoformat()}] Tried to start "
            f"{self.timer_name} but it was already running."
        )


@dataclass
class TimerNotRunningError(AbstractTimerError):
    """Error raised when one tries to click (measure or stop) `Timer`
    that's not running.
    """

    action: Action

    def __post_init__(self) -> None:
        self.message = (
            f"[{self.timestamp.isoformat()}] Tried to click `{self.action}` "
            f"on {self.timer_name} but it wasn't running."
        )
