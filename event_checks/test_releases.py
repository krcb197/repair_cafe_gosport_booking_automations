"""
Test the release are correctly configured to go on and off sale. In Tito terminology a release
is a opportunity to buy tickets

In order to encourage people not to book up the 10:30 slot, more tickets are released for the other
slots first (the so-called early bird phase) before everything goes on general release.

tickets release in two increments:
- early bird and bike slot 2 - on the previous 2nd Saturday, the logic is that people
  attending the previous event can book for the next
- non-early bird and bike slot 1 - two weeks before the event
"""
import datetime
import pytest
from dataclasses import dataclass, field

from pytito.admin import Event, Release

from .test_event import second_saturday

@dataclass
class RCGEventWithDates:
    event: Event
    early_bird_on_sale: datetime.datetime = field(init=False)
    early_bird_to_general_on_sale: datetime.datetime = field(init=False)

    @property
    def __previous_second_saturday(self) -> datetime.date:

        month = self.event.start_at.month
        year = self.event.start_at.year

        month -= 1
        if month == 0:
            year -= 1
            month = 12

        return second_saturday(year=year, month=month)

    def __post_init__(self):
        event_start_time = self.event.start_at

        one_min_after_midnight = datetime.time(hour=0, minute=1, second=0, tzinfo=datetime.timezone.utc)

        self.early_bird_on_sale = datetime.datetime.combine(
            self.__previous_second_saturday,
            one_min_after_midnight)
        self.early_bird_to_general_on_sale = datetime.datetime.combine(
            event_start_time.date() - datetime.timedelta(days=14),
            one_min_after_midnight)

    def find_release(self, title: str) -> Release:
        for release in self.event.releases.values():
            if release.title == title:
                return release
        raise IndexError(f'Failed to find release titled: {title}')

@pytest.fixture
def future_event_with_release_dates(future_events):
    yield RCGEventWithDates(future_events)

@pytest.mark.parametrize('booking_slot', range(3),ids=[f'Booking Slot {idx+1}' for idx in range(3)])
def test_general_repair_releases(future_event_with_release_dates,booking_slot):
    """
    Check the configuration of a general repair booking release. This has 3 slots in the time
    period are named as follows:
    - Repair Cafe Guest - General Repair - Booking Slot 1 (10:30) - Early Bird
    - Repair Cafe Guest - General Repair - Booking Slot 1 (10:30)
    - Repair Cafe Guest - General Repair - Booking Slot 2 (11:15) - Early Bird
    - Repair Cafe Guest - General Repair - Booking Slot 2 (11:15)
    - Repair Cafe Guest - General Repair - Booking Slot 3 (12:00) - Early Bird
    - Repair Cafe Guest - General Repair - Booking Slot 3 (12:00)

    The name is based on the start time of the event (which is checked in a previous test), so
    for an 11:30 starting event these all increment by one hour
    """
    release_start_time = future_event_with_release_dates.event.start_at + (booking_slot * datetime.timedelta(minutes=45))
    main_release_title = (f'Repair Cafe Guest - General Repair - '
                          f'Booking Slot {booking_slot + 1} ({release_start_time:%H:%M})')
    main_release = future_event_with_release_dates.find_release(title=main_release_title)

    assert main_release.start_at is not None
    assert main_release.start_at == future_event_with_release_dates.early_bird_to_general_on_sale
    assert main_release.end_at is None
    assert not main_release.secret

    early_bird_release_title = main_release_title + ' - Early Bird'
    early_bird_release = future_event_with_release_dates.find_release(title=early_bird_release_title)

    assert early_bird_release.start_at is not None
    assert early_bird_release.start_at == future_event_with_release_dates.early_bird_on_sale
    assert early_bird_release.end_at is not None
    assert early_bird_release.end_at == future_event_with_release_dates.early_bird_to_general_on_sale
    assert not early_bird_release.secret


@pytest.mark.parametrize('booking_slot', range(2),
                         ids=[f'Booking Slot {idx + 1}' for idx in range(2)])
def test_bike_repair_releases(future_event_with_release_dates, booking_slot):
    """
    Check the configuration of a bike repair booking release. This has 2 slots in the time
    period, as bike repair normally take longer, are named as follows:
    - Repair Cafe Guest - Bike Repair - Booking Slot 1 (10:30)
    - Repair Cafe Guest - Bike Repair - Booking Slot 2 (11:45)

    The name is based on the start time of the event (which is checked in a previous test), so
    for an 11:30 starting event these all increment by one hour

    The bike repair don't have an early bird option instead the 2nd slot is released in the
    early bird time and the first slot releases at the same time as the general release of the
    tickets
    """
    release_start_time = future_event_with_release_dates.event.start_at + (booking_slot * datetime.timedelta(hours=1, minutes=15))
    bike_release_title = (f'Repair Cafe Guest - Bike Repair - '
                          f'Booking Slot {booking_slot + 1} ({release_start_time:%H:%M})')
    bike_release = future_event_with_release_dates.find_release(title=bike_release_title)

    assert bike_release.start_at is not None
    if booking_slot == 0:
       assert bike_release.start_at == future_event_with_release_dates.early_bird_to_general_on_sale
    elif booking_slot == 1:
        assert bike_release.start_at == future_event_with_release_dates.early_bird_on_sale
    else:
        raise RuntimeError(f'Unhandled {booking_slot=}')
    assert bike_release.end_at is None

    assert not bike_release.secret

def test_volunteer_releases(future_event_with_release_dates):
    """
    A special ticket release that allows volunteers to book in an item
    """
    volunteer_release = future_event_with_release_dates.find_release(title='Volunteer Repair')
    assert volunteer_release.start_at is not None
    assert volunteer_release.start_at == future_event_with_release_dates.early_bird_on_sale
    assert volunteer_release.end_at is None
    assert volunteer_release.secret
