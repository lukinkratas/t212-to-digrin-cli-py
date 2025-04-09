import getpass
from datetime import datetime
from functools import wraps
from time import perf_counter


def get_username():
    return getpass.getuser()


def track_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'{datetime.now()} {get_username()} called {func.__name__}.')
        print(f'  {args=}')
        print(f'  {kwargs=}')

        result = func(*args, **kwargs)

        print(f'{func.__name__} finished.\n  {result=}')

        return result

    return wrapper


def track_time_performance(n=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f'{func.__name__} running {n}time(s) started.')
            start_time = perf_counter()

            for _ in range(n):
                result = func(*args, **kwargs)

            elapsed_time = perf_counter() - start_time
            print(f'{func.__name__} finished, took: {elapsed_time:0.8f} seconds.')

            return result

        return wrapper

    return decorator
