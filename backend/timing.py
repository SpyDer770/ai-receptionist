import time
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Optional


class LatencyTracker:
    def __init__(self):
        self.ai_ms = 0.0
        self.db_ms = 0.0
        self.db_calls = 0


_current: ContextVar[Optional[LatencyTracker]] = ContextVar(
    "latency_tracker", default=None
)


def start_tracking() -> LatencyTracker:
    tracker = LatencyTracker()
    _current.set(tracker)
    return tracker


@contextmanager
def measure_ai():
    start = time.perf_counter()
    try:
        yield
    finally:
        tracker = _current.get()
        if tracker is not None:
            tracker.ai_ms += (time.perf_counter() - start) * 1000


def timed_db(func):
    """Decorator: adds this function's runtime to the current request's DB total."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            tracker = _current.get()
            if tracker is not None:
                tracker.db_ms += (time.perf_counter() - start) * 1000
                tracker.db_calls += 1
    return wrapper