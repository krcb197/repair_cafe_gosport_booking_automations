"""
This module extends the pytito mode to provide specific behaviours for a Repair Cafe Gosport
TITO event, including event duplication and setup
"""

from typing import Any, Optional
from operator import attrgetter
from dataclasses import dataclass, field
import datetime
from itertools import product
from collections.abc import Iterator
from abc import ABC

import requests

from pytito import AdminAPI
from pytito.admin import Account
from pytito.admin import Ticket
from pytito.admin import Event

from .date_operations import second_saturday, one_min_after_midnight

@dataclass
class RCGActivityDef(ABC):
    """
    Abstract Base Class for a Repair Cafe Gosport Tito Event Activity
    """
    event_start_timestamp: datetime.datetime
    name: str = field(init=False)
    start: datetime.datetime = field(init=False)
    end: datetime.datetime = field(init=False)

@dataclass
class RCGReleaseDef(ABC):
    """
    Abstract Base Class for a Repair Cafe Gosport Tito Event Release. A Release is block of
    tickets that can go (On-sale and Off-sale)
    """
    event_start_time: datetime.time
    early_bird_on_sale: datetime.datetime
    early_bird_to_general_on_sale: datetime.datetime
    slot_start_time : datetime.time = field(init=False)
    on_sale: datetime.datetime = field(init=False)
    off_sale: Optional[datetime.datetime] = field(init=False)
    release_title: str = field(init=False)
    release_slug_prefix : str = field(init=False)
    preferred_release_slug: str = field(init=False)

@dataclass
class RCGBikeRepairReleaseDef(RCGReleaseDef):
    """
    Class for a Repair Cafe Gosport Tito Event Release Bike Repair Ticket Release. A Release
    is block of tickets that can go (On-sale and Off-sale)

    There are 2 1-hour booking slots at a Repair Cafe Gosport Event.
    """
    slot: int

    def __post_init__(self):
        if not 1 <= self.slot <= 2:
            raise ValueError(f'Slot should be in the range 1 to 2, got {self.slot}')
        self.slot_start_time = (datetime.datetime.combine(datetime.date.today(), self.event_start_time) + (datetime.timedelta(hours=1, minutes=15) * (self.slot - 1))).time()
        if self.slot == 2:
            self.on_sale = self.early_bird_on_sale
            self.off_sale = None
        else:
            self.on_sale = self.early_bird_to_general_on_sale
            self.off_sale = None
        self.release_title = f'Repair Cafe Guest - Bike Repair - Booking Slot {self.slot} ({self.slot_start_time:%H:%M})'
        self.preferred_release_slug = f'repair-cafe-guest-bike-repair-booking-slot-{self.slot}'
        self.release_slug_prefix = self.preferred_release_slug

@dataclass
class RCGGeneralRepairReleaseDef(RCGReleaseDef):
    """
    Class for a Repair Cafe Gosport Tito Event Release General Repair Ticket Release. A Release
    is block of tickets that can go (On-sale and Off-sale)

    There are 3 45-minutes booking slots at a Repair Cafe Gosport Event. The tickets go "on-sale"
    in two batches:
    - so called 'Early Bird' with reduced numbers in the earlier part of the session in order to
      encourage guests to come later
    - A general release where everything is available

    """
    slot: int
    early_bird: bool

    def __post_init__(self):
        if not 1 <= self.slot <= 3:
            raise ValueError(f'Slot should be in the range 1 to 3, got {self.slot}')
        self.slot_start_time = (datetime.datetime.combine(datetime.date.today(), self.event_start_time) + (datetime.timedelta(minutes=45) * (self.slot - 1))).time()
        if self.early_bird:
            self.on_sale = self.early_bird_on_sale
            self.off_sale = self.early_bird_to_general_on_sale
        else:
            self.on_sale = self.early_bird_to_general_on_sale
            self.off_sale = None
        self.release_title = f'Repair Cafe Guest - General Repair - Booking Slot {self.slot} ({self.slot_start_time:%H:%M})'
        self.preferred_release_slug = f'repair-cafe-guest-general-repair-booking-slot-{self.slot}'
        self.release_slug_prefix = self.preferred_release_slug
        if self.early_bird:
            self.release_title += ' - Early Bird'
            self.preferred_release_slug += '-early-bird'

@dataclass
class RCGVolunteerRepairReleaseDef(RCGReleaseDef):
    """
    Class for a Repair Cafe Gosport Tito Event Release Volunteer Repair Ticket Release. A Release
    is block of tickets that can go (On-sale and Off-sale)
    """
    def __post_init__(self):
        self.slot_start_time = (datetime.datetime.combine(datetime.date.today(), self.event_start_time)).time()
        self.on_sale = self.early_bird_on_sale
        self.off_sale = None
        self.release_title = f'Volunteer Repair'
        self.preferred_release_slug = f'volunteer-repair'
        self.release_slug_prefix = self.preferred_release_slug

@dataclass
class RCGBikeRepairActivityDef(RCGActivityDef):
    """
    Class for a Repair Cafe Gosport General Repair Activity.
    """
    slot: int

    def __post_init__(self):
        self.start = self.event_start_timestamp + (datetime.timedelta(hours=1, minutes=15) * (self.slot - 1))
        self.end = self.start + datetime.timedelta(minutes=60)
        self.name = f'Bike Repair Booking Slot {self.slot}'

@dataclass
class RCGGeneralRepairActivityDef(RCGActivityDef):
    """
    Class for a Repair Cafe Gosport General Repair Activity. The activity is needed to limit the
    total number of tickets over the Early Bird and General Release.
    """
    slot: int

    def __post_init__(self):
        self.start = self.event_start_timestamp + (datetime.timedelta(minutes=45) * (self.slot - 1))
        self.end = self.start + datetime.timedelta(minutes=45)
        self.name = f'General Repair Booking Slot {self.slot}'

@dataclass
class RCGEventDef:
    """
    The Definition of a Repair Cafe Gosport event. This is intended to be used to hold the
    configuration of a Tito Event.
    """
    month: int
    year: int
    event_start_time: datetime.time
    event_start_timestamp: datetime.datetime = field(init=False)
    event_end_timestamp: datetime.datetime = field(init=False)
    early_bird_on_sale: datetime.datetime = field(init=False)
    early_bird_to_general_on_sale: datetime.datetime = field(init=False)
    event_title: str = field(init=False)
    preferred_event_slug: str = field(init=False)

    def __post_init__(self):
        if not 1 <= self.month <= 12:
            raise ValueError(f'Month should be in the range 1 to 12, got {self.month}')
        event_state_date = self.__second_saturday

        # Some tickets go "on-sale" after the previous event to allow guests to book their follow
        # up visit
        self.early_bird_on_sale = datetime.datetime.combine(
            self.__previous_second_saturday,
            one_min_after_midnight)
        # To avoid too manay guests booking and not turning up, the main batch of tickets only
        # becomes available 2 weeks before the event
        self.early_bird_to_general_on_sale = datetime.datetime.combine(
            event_state_date - datetime.timedelta(days=14),
            one_min_after_midnight)

        self.event_start_timestamp = datetime.datetime.combine(
            event_state_date, self.event_start_time)
        self.event_end_timestamp = self.event_start_timestamp + datetime.timedelta(hours=2, minutes=30)

        self.event_title = f'Repair Café {self.event_start_timestamp:%B} {self.event_start_timestamp:%Y}'
        self.preferred_event_slug = 'repair-cafe-' + self.event_start_timestamp.strftime('%B').lower() + '-' + self.event_start_timestamp.strftime('%Y')

    @property
    def __second_saturday(self) -> datetime.date:
        """
        Repair Cafe Gosport events happen on the 2nd saturday of the month

        Determine the date of the 2nd for a given month and year
        """
        return second_saturday(year=self.year, month=self.month)

    @property
    def __previous_second_saturday(self) -> datetime.date:
        """
        Provides the date of the previous 2nd Saturday
        """

        year = self.year

        month = self.month - 1
        if month == 0:
            year -= 1
            month = 12

        return second_saturday(year=year, month=month)

    @property
    def releases(self) -> Iterator[RCGReleaseDef]:
        """
        Iterator to go through all the Event Ticket Releases:
        - General Repair 3 slots with Early Bird ticket releases
        - Bike Repair
        - A secret volunteer ticket so our volunteers can book in their own items
        """
        for slot, early_bird in product(range(3), [True, False]):
            yield RCGGeneralRepairReleaseDef(
                event_start_time=self.event_start_time,
                early_bird_on_sale=self.early_bird_on_sale,
                early_bird_to_general_on_sale=self.early_bird_to_general_on_sale,
                slot=slot + 1,
                early_bird=early_bird,
            )
        for slot in range(2):
            yield RCGBikeRepairReleaseDef(
                event_start_time=self.event_start_time,
                early_bird_on_sale=self.early_bird_on_sale,
                early_bird_to_general_on_sale=self.early_bird_to_general_on_sale,
                slot=slot + 1, )
        yield RCGVolunteerRepairReleaseDef(
            event_start_time=self.event_start_time,
            early_bird_on_sale=self.early_bird_on_sale,
            early_bird_to_general_on_sale=self.early_bird_to_general_on_sale)

    @property
    def activities(self) -> Iterator[RCGActivityDef]:
        """
        An iterator for all the event activities
        """
        for slot in range(3):
            yield RCGGeneralRepairActivityDef(event_start_timestamp=self.event_start_timestamp,
                                           slot=slot + 1)
        for slot in range(2):
            yield RCGBikeRepairActivityDef(event_start_timestamp=self.event_start_timestamp,
                                           slot=slot + 1)

class RCG_Ticket(Ticket):
    """
    Extension to the Ticket Class provided by pyTito with the features of a book at Repair
    Cafe Gosport
    """

    @classmethod
    def build_from_ticket(cls, ticket: Ticket) -> 'RCG_Ticket':
        return cls(account_slug=ticket._account_slug,
                   event_slug=ticket._event_slug,
                   ticket_slug=ticket._ticket_slug,
                   allow_automatic_json_retrieval=True)


    @property
    def repair_type(self) -> str:
        for answer in self.answers:
            if answer['question_title'] == 'What type of Broken Thing do you want help with':
                if answer['primary_response'] == 'other':
                    if answer['alternate_response'] is not None:
                        return 'Other: ' + answer['alternate_response']
                    return 'Other'
                return answer['primary_response']
        return None

    @property
    def repair_item(self) -> str:
        for answer in self.answers:
            if answer['question_title'] == 'Description of the Broken Things':
                return answer['primary_response']
        return None

    @property
    def repair_fault(self) -> str:
        for answer in self.answers:
            if answer['question_title'] == 'Description of the Fault':
                return answer['primary_response']
        return None

    @property
    def _repair_picture(self) -> dict[str, Any]:
        for answer in self.answers:
            if answer['question_title'] == 'Picture':
                return answer
        return None

    @property
    def repair_picture_present(self):
        if self._repair_picture is not None:
            if self._repair_picture['download_url'] is None:
                return False
            return True
        return False

    def retrieve_repair_picture(self, filename):
        if not self.repair_picture_present:
            raise RuntimeError('No picture available to download')
        url = self._repair_picture['download_url']
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f'request failed with status code {response.status_code}')
        with open(filename, mode='wb') as fid:
            fid.write(response.content)

    @property
    def phone_number(self) -> str:
        for answer in self.answers:
            if answer['question_title'] == 'Phone Number':
                return answer['primary_response']
        return None

    @property
    def post_code(self) -> str:
        for answer in self.answers:
            if answer['question_title'] == 'Post Code':
                return answer['primary_response']
        return None

class RCG_TITO_API(Account):
    """
    Extension to the Account Class which goes directly to the repair-cafe-gosport slug
    """
    RCG_ACCOUNT_SLUG = 'repair-cafe-gosport'

    def __init__(self, api_key: Optional[str] = None):
        tito_admin_access = AdminAPI(api_key=api_key)
        if self.RCG_ACCOUNT_SLUG not in tito_admin_access.accounts:
            raise RuntimeError(f'No access to the {self.RCG_ACCOUNT_SLUG} account')
        super().__init__(account_slug=self.RCG_ACCOUNT_SLUG, api_key=api_key)

    @property
    def newest_event(self) -> Event:
        """
        Return the chronologically latest of the upcoming events
        """

        def include_event(event: Event) -> bool:
            return event.start_at is not None and event.title.startswith('Repair')

        upcoming_events = list(filter(include_event, self.events.values()))
        upcoming_events.sort(key=attrgetter('start_at'))
        return upcoming_events[-1]

    def new_event(self, month: int, year: int, start_time: datetime.time) -> Event:
        """
        Make a new event by duplicating newest event and then configuring the times. The Newest
        event is typically the last one to have been setup, so has any tweaks to the wording.

        This function can also be used to update the event (if it has already been created), so
        if the event slug already exists, it will skip the duplication step

        :param month: Event Month e.g 5 for May
        :param year: Event Year e.g. 2025
        :param start_time:
        :return: The event created
        """
        event_definition = RCGEventDef(year=year, month=month, event_start_time=start_time)
        if event_definition.preferred_event_slug in self.events:
            print(f'Event slug {event_definition.preferred_event_slug} already in use')
            event = self.events[event_definition.preferred_event_slug]
        else:
            candidate_event_to_clone = self.newest_event
            print(f'planning to clone {candidate_event_to_clone.title}')
            event = candidate_event_to_clone.duplicate_event(title=event_definition.event_title,
                                                             slug=event_definition.preferred_event_slug)

        event.start_at = event_definition.event_start_timestamp
        event.end_at = event_definition.event_end_timestamp

        for release_def in event_definition.releases:
            if release_def.preferred_release_slug in event.releases:
                release = event.releases[release_def.preferred_release_slug]
            else:
                for release_slug, release in event.releases.items():
                    if isinstance(release_def, RCGGeneralRepairReleaseDef):
                        if release_def.early_bird:
                            if release_slug.startswith(release_def.release_slug_prefix) and release_slug.endswith('early-bird'):
                                release._update_slug(release_def.preferred_release_slug)
                                break
                        else:
                            if release_slug.startswith(release_def.release_slug_prefix) and not release_slug.endswith('early-bird'):
                                release._update_slug(release_def.preferred_release_slug)
                                break
                    else:
                        if release_slug.startswith(release_def.release_slug_prefix):
                            release._update_slug(release_def.preferred_release_slug)
                            break
                else:
                    raise ValueError(f'Failed to find release to match {release_def.title}')

            release.title = release_def.release_title
            release.end_at = None
            release.start_at = None
            release.end_at = release_def.off_sale
            release.start_at = release_def.on_sale

        for activity_def in event_definition.activities:
            for activity in event.activities:
                if activity.name == activity_def.name:
                    break
            else:
                raise ValueError(f'Failed to find activity to match {activity_def.name}')
            activity.end_at = None
            activity.start_at = activity_def.start
            activity.end_at = activity_def.end

        return event
