from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from functools import wraps
from typing import Union

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.tz import gettz


def _convert_datetime(val):
    """Try to convert a value to datetime; return as-is on failure."""
    try:
        if isinstance(val, date) and not isinstance(val, datetime):
            return datetime.combine(val, datetime.min.time())
        return parse(val)
    except Exception:
        return val


def timeparser(func):
    """All params will first try to converted to datetime objects through this decorator."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        parsed_args = tuple(_convert_datetime(a) for a in args)
        parsed_kwargs = {k: _convert_datetime(v) for k, v in kwargs.items()}
        return func(*parsed_args, **parsed_kwargs)

    return wrapper


class Time:
    @staticmethod
    def tzone(tz=None):
        if tz is not None:
            if isinstance(tz, int):
                return timezone(timedelta(hours=tz))
            elif isinstance(tz, str):
                return gettz(tz)
        return None

    @staticmethod
    def now(format_=None, tz=None) -> Union[datetime, str]:
        dt = datetime.now(tz=Time.tzone(tz))
        return dt.strftime(format_) if format_ else dt

    @staticmethod
    def today() -> date:
        return Time.now().date()

    @staticmethod
    def from_timestamp(timestamp, format_=None, tz=None) -> Union[datetime, str]:
        ts = Decimal(timestamp)
        if len(str(ts)) > 10 and "." not in str(ts):
            ts /= 1000
        dt = datetime.fromtimestamp(float(ts), tz=Time.tzone(tz))
        return dt.strftime(format_) if format_ else dt

    @staticmethod
    @timeparser
    def to_timezone(dt, tz) -> datetime:
        return dt.astimezone(tz=Time.tzone(tz))

    @staticmethod
    @timeparser
    def timestamp(dt=None, ms=False) -> int:
        dt = dt or datetime.now()
        ts = dt.timestamp()
        return int(ts * 1_000) if ms else int(ts)

    @staticmethod
    @timeparser
    def format(dt, format_) -> str:
        return dt.strftime(format_)

    @staticmethod
    def strptime(time_str: str, format_: str) -> datetime:
        return datetime.strptime(time_str, format_)

    @staticmethod
    @timeparser
    def delta(
        dt=None,
        format_=None,
        years: int = 0,
        months: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
    ) -> Union[datetime, str]:
        dt = dt or datetime.now()
        result = dt + relativedelta(
            years=int(years),
            months=int(months),
            days=int(days),
            hours=int(hours),
            minutes=int(minutes),
            seconds=int(seconds),
            microseconds=int(microseconds),
        )
        return result.strftime(format_) if format_ else result

    @staticmethod
    @timeparser
    def in_range(
        dt,
        ref_time,
        *,
        years: int = 0,
        months: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
    ) -> bool:
        duration = relativedelta(
            years=int(years),
            months=int(months),
            days=int(days),
            hours=int(hours),
            minutes=int(minutes),
            seconds=int(seconds),
            microseconds=int(microseconds),
        )
        return dt - duration <= ref_time <= dt + duration

    @staticmethod
    @timeparser
    def is_equal(*times, skip_ms: bool = True) -> bool:
        timestamps = [t.timestamp() for t in times]
        first = timestamps[0]
        if skip_ms:
            return all(int(ts) == int(first) for ts in timestamps)
        return all(ts == first for ts in timestamps)
