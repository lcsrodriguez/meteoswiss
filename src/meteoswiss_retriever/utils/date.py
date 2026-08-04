"""Utils funcs for date"""

from datetime import date, datetime

from pytz import UTC  # type: ignore[import-untyped]

from meteoswiss_retriever.constants import CURRENT_TZ


def get_datetime_from_str(str_datetime: str | None = None) -> datetime:
    """
    Function to convert a string datetime to real `datetime` object
    :param str_datetime: String format of datetime
    :type str_datetime: str | None
    :return: Datetime object
    :rtype: datetime
    """
    if str_datetime is None:
        return datetime.now().replace(tzinfo=UTC).astimezone(tz=CURRENT_TZ)
    return (
        datetime.strptime(str_datetime, "%Y%m%d%H%M")
        .replace(tzinfo=UTC)
        .astimezone(tz=CURRENT_TZ)
    )


def get_date_from_str(str_date: str | None = None) -> date:
    """
    Function to convert a string date to real `date` object
    :param str_date: String format of date
    :type str_date: str | None
    :return: Date object
    :rtype: date
    """
    if str_date is None:
        return datetime.today().replace(tzinfo=UTC).astimezone(tz=CURRENT_TZ)
    return (
        datetime.strptime(str_date, "%Y%m%d")
        .replace(tzinfo=UTC)
        .astimezone(tz=CURRENT_TZ)
        .date()
    )


def get_datetime_from_iso_str(str_datetime: str | None = None) -> datetime:
    """
    Function to convert a string datetime (in string ISO format) to real `datetime` object
    :param str_datetime: String format of datetime
    :type str_datetime: str | None
    :return: Datetime object
    :rtype: datetime
    """
    if str_datetime is None:
        return datetime.now().replace(tzinfo=UTC).astimezone(tz=CURRENT_TZ)
    return (
        datetime.fromisoformat(str_datetime)
        .replace(tzinfo=UTC)
        .astimezone(tz=CURRENT_TZ)
    )
