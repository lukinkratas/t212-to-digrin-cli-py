import getpass
import statistics
from datetime import datetime, timedelta
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


def track_time_performance(n: int = 1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            run_times = []

            print(f'{func.__name__} running {n} time(s) started.')
            total_start_time = perf_counter()

            for idx in range(1, n + 1):
                print(f'  {func.__name__} run no.{idx} started.')
                run_start_time = perf_counter()

                result = func(*args, **kwargs)

                run_elapsed_time = perf_counter() - run_start_time
                run_times.append(run_elapsed_time)
                print(f'  {func.__name__} run no.{idx} finished.')
                print(f'  {timedelta(seconds=run_elapsed_time)}.\n')

            total_elapsed_time = perf_counter() - total_start_time
            print(f'{func.__name__} running {n} time(s) finished.')
            print(f'  Total: {timedelta(seconds=total_elapsed_time)}')
            print(f'  Average: {timedelta(seconds=statistics.mean(run_times))}')

            return result

        return wrapper

    return decorator
