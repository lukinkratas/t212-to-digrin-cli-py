import getpass
import logging
import statistics
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from time import perf_counter
from typing import Any


def init_logger() -> logging.Logger:
    logging.basicConfig(
        format='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        level=logging.DEBUG,
    )

    return logging.getLogger('t212_to_digrin')


logger: logging.Logger = init_logger()


def get_username() -> str:
    return getpass.getuser()


def get_func_name_and_args(
    func: Callable[..., Any], args: tuple[Any, ...]
) -> tuple[str, tuple[Any, ...]]:
    # check if first argument is class instance (self)
    if hasattr(args[0], func.__name__):
        func_name = f'{args[0].__class__.__name__}.{func.__name__}'
        return func_name, args[1:]

    return func.__name__, args


def track_args(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func_name, args_copy = get_func_name_and_args(func, args)

        logger.debug(
            f'{get_username()} called {func_name}().\n  args={args_copy}\n  {kwargs=}'
        )
        result = func(*args, **kwargs)
        logger.debug(f'{func_name} finished.\n  {result=}\n')

        return result

    return wrapper


def track_time_performance(n: int = 1) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name, _ = get_func_name_and_args(func, args)
            run_times = []

            print(f'{func_name} running {n} time(s) started.')
            total_start_time = perf_counter()

            for idx in range(1, n + 1):
                logger.debug(f'  {func_name} run no.{idx} started.')
                run_start_time = perf_counter()

                result = func(*args, **kwargs)

                run_elapsed_time = perf_counter() - run_start_time
                run_times.append(run_elapsed_time)
                run_elapsed_time_td = timedelta(seconds=run_elapsed_time)
                logger.debug(
                    f'  {func_name} run no.{idx} finished.\n  {run_elapsed_time_td}'
                )

            total_elapsed_time = perf_counter() - total_start_time
            total_elapsed_time_td = timedelta(seconds=total_elapsed_time)
            avg_elapsed_time_td = timedelta(seconds=statistics.mean(run_times))
            logger.debug(
                f'{func_name} running {n} time(s) finished.\n  total={total_elapsed_time_td}\n  average={avg_elapsed_time_td}'  # noqa: E501
            )

            return result

        return wrapper

    return decorator
