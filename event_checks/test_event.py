import calendar
import re
import datetime

_event_name_re = re.compile(r"^Repair Café (?P<month>[A-Za-z]+) (?P<year>\d{4})$")

import pytest

from pytito.admin import AdminAPI

repair_cafe_gosport_tito = AdminAPI().accounts['repair-cafe-gosport']

def second_saturday(year, month) -> datetime.date:
    """
    Repair Cafe Gosport events happen on the 2nd saturday of the month

    Determine the date of the 2nd for a given month and year
    """
    if not 1 <= month <= 12:
        raise ValueError(f'Month should be in the range 1 to 12, got {month}')
    cal = calendar.monthcalendar(year, month)
    saturdays = [week[calendar.SATURDAY] for week in cal
                 if week[calendar.SATURDAY] != 0]
    return datetime.date(year, month, saturdays[1])

def next_second_saturday() -> datetime.date:
    """
    Find the next second saturday relative to today
    """
    year = datetime.date.today().year
    month = datetime.date.today().month

    ss = second_saturday(year, month)
    if ss > datetime.date.today():
        return ss

    # move to next month
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    return second_saturday(year, month)

def test_event_conf(future_events):
    """
    Check the configuration of all the events
    """
    re_match = _event_name_re.match(future_events.title)
    assert re_match is not None, "String does not match expected format"

    month_name  = re_match.group("month")
    year = int(re_match.group("year"))
    assert future_events.live is True

    # Convert month name to month number
    month_number = datetime.datetime.strptime(month_name, "%B").month

    expected_date = second_saturday(month=month_number, year=year)
    assert future_events.start_at.date() == expected_date
    assert future_events.end_at.date() == expected_date

    # The event should be 2.5 hours long, it may start at either 10:30 or 11:30
    event_length = future_events.end_at - future_events.start_at
    assert event_length == datetime.timedelta(hours=2, minutes=30)

    # check the event starts at either 10:30 or 11:30
    assert future_events.start_at.time() in [datetime.time(hour=10, minute=30),
                                            datetime.time(hour=11, minute=30)]

