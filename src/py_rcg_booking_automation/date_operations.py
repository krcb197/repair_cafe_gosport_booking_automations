"""
A set of date helper functions. This is all based on Repair Cafe Gosport events happening on
the 2nd saturday of the month
"""
import datetime
import calendar
from collections.abc import Iterator

def second_saturday(year, month) -> datetime.date:
    """
    Determine the date of the 2nd Saturday for a given month and year
    """
    if not 1 <= month <= 12:
        raise ValueError(f'Month should be in the range 1 to 12, got {month}')
    cal = calendar.monthcalendar(year, month)
    saturdays = [week[calendar.SATURDAY] for week in cal
                 if week[calendar.SATURDAY] != 0]
    return datetime.date(year, month, saturdays[1])

def previous_second_saturday(month, year) -> datetime.date:
    """
    Determine the date of the previous months 2nd Saturday.
    """
    month -= 1
    if month == 0:
        year -= 1
        month = 12

    return second_saturday(year=year, month=month)

one_min_after_midnight = datetime.time(hour=0, minute=1, second=0, tzinfo=datetime.timezone.utc)

def iter_months(start_date: datetime.date, end_date: datetime.date):
    """
    An iterator that yields the month and year between a start date and an end date,
    excluding August (because Repair Cafe Gosport takes a break that month)
    """
    year = start_date.year
    month = start_date.month

    while (year, month) <= (end_date.year, end_date.month):
        if month != 8:
            # Repair Cafe Gosport does not operate in August
            yield year, month

        month += 1
        if month > 12:
            month = 1
            year += 1


def event_dates(start_date: datetime.date, end_date: datetime.date) -> Iterator[datetime.date]:
    """
    An Iterator that yields the dates of Repair Cafe Gosport Events between two dates
    """
    for year, month in iter_months(start_date, end_date):
        yield second_saturday(year=year, month=month)
