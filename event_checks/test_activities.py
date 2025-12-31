"""
Test the activities are correctly configured
"""

import datetime
import pytest

from pytito.admin import Event, Activity

def find_activity(event: Event, name: str) -> Activity:
    for activity in event.activities:
        if activity.name == name:
            return activity
    raise IndexError(f'Failed to find activity named: {name}')

@pytest.mark.parametrize('booking_slot', range(3),ids=[f'Booking Slot {idx+1}' for idx in range(3)])
def test_general_repair_activities(future_events,booking_slot):
    """
    Check the configuration of a general repair booking activities. This has 3 slots in the time
    period are named as follows:
    - General Repair Booking Slot 1
    - General Repair Booking Slot 2
    - General Repair Booking Slot 3
    """
    activity = find_activity(event=future_events,
                             name=f'General Repair Booking Slot {booking_slot+1}')
    activity_start_time = future_events.start_at + (booking_slot * datetime.timedelta(minutes=45))
    activity_end_time = activity_start_time + datetime.timedelta(minutes=45)
    assert activity.start_at == activity_start_time
    assert activity.end_at == activity_end_time

@pytest.mark.parametrize('booking_slot', range(2),ids=[f'Booking Slot {idx+1}' for idx in range(2)])
def test_bike_repair_activities(future_events,booking_slot):
    """
    Check the configuration of a general repair booking activities. This has 2 slots in the time
    period are named as follows:
    - Bike Repair Booking Slot 1
    - Bike Repair Booking Slot 2
    """
    activity = find_activity(event=future_events,
                             name=f'Bike Repair Booking Slot {booking_slot+1}')
    activity_start_time = future_events.start_at + (booking_slot * datetime.timedelta(hours=1, minutes=15))
    activity_end_time = activity_start_time + datetime.timedelta(minutes=60)
    assert activity.start_at == activity_start_time
    assert activity.end_at == activity_end_time