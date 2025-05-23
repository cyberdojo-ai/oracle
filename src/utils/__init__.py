from datetime import timezone, datetime
from functools import wraps


def singleton(cls):
    """
    synchronous singleton decorator for classes
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

def run_once(
    func: callable,
):
    """
    Run a function only once.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper

def current_utc_time() -> datetime:
    return datetime.now(tz=timezone.utc)
