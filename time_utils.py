from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_first_day_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1)


def get_first_day_of_next_month(dt: datetime) -> datetime:
    next_month_dt = dt + relativedelta(months=1)  # works even for Jan and Dec
    return next_month_dt.replace(day=1)
