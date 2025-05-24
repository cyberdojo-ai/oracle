"""Gevent based crontab implementation"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Coroutine, Literal, Callable, Awaitable
import gevent
from typing import TypeVar

class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item) -> Literal[True]:
        return True

allMatch = AllMatch()

# Some utility classes / functions first
def conv_to_set(obj: int | list[int] | tuple[int] | range | AllMatch) -> set:
    """Converts to set allowing single integer to be provided"""
    if isinstance(obj, (int)):
        return set([obj])  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj


T = TypeVar("T")
Action = Callable[[T], Awaitable[None]] | Callable[[T], Any]

class Event(object):
    """The Actual Event Class"""

    def __init__(self,
        action: Action,
        minute: AllMatch | int | set = allMatch,
        hour: AllMatch | int | set = allMatch,
        day: AllMatch | int | set = allMatch,
        month: AllMatch | int | set = allMatch,
        daysofweek: AllMatch | int | set = allMatch,
        args: T =(),
        kwargs: T ={}
    ) -> None:
        self.mins = conv_to_set(minute)
        self.hours = conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.daysofweek = conv_to_set(daysofweek)
        self.action = action
        self.args = args
        self.kwargs = kwargs

        if callable(self.action) and isinstance(self.action, Coroutine):
            raise TypeError("Coroutine objects are not callable. Did you mean to pass a coroutine function?")
        self.async_event = callable(self.action) and asyncio.iscoroutinefunction(self.action)

    def matchtime(self, t1: datetime) -> bool:
        """Return True if this event should trigger at the specified datetime"""
        return ((t1.minute     in self.mins) and
                (t1.hour       in self.hours) and
                (t1.day        in self.days) and
                (t1.month      in self.months) and
                (t1.weekday()  in self.daysofweek))

    def check(self, t: datetime) -> None:
        """Check and run action if needed"""

        if self.matchtime(t):
            result = self.action(*self.args, **self.kwargs)
            if self.async_event:
                # If the action is a coroutine, run it in the event loop
                asyncio.run(result)

class CronTab(object):
    """The crontab implementation"""

    def __init__(self,
        *events: list[Event],
    ) -> None:
        self.events: list[Event] = events

    def _check(self) -> None:
        """Check all events in separate greenlets"""

        t1 = datetime(*datetime.now().timetuple()[:5])
        for event in self.events:
            gevent.spawn(event.check, t1)

        t1 += timedelta(minutes=1)
        s1 = (t1 - datetime.now()).seconds + 1
        job = gevent.spawn_later(s1, self._check)

    def run(self) -> None:
        """Run the cron forever"""

        self._check()
        while True:
            gevent.sleep(60)

default_crontab = CronTab()

__all__ = [
    "Event",
    "CronTab",
    "allMatch",
    "default_crontab",
]
