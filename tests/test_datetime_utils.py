from datetime import datetime

from custom_utils import datetime_utils

default_df: datetime = datetime(2024, 8, 12)


def test_get_first_day_of_month() -> None:
    assert datetime_utils.get_first_day_of_month(default_df) == datetime(2024, 8, 1)


def test_get_first_day_of_next_month() -> None:
    assert datetime_utils.get_first_day_of_next_month(default_df) == datetime(
        2024, 9, 1
    )
