


from itertools import chain
from typing import TypedDict
from datetime import date
from pathlib import Path

import pandas as pd

from .rcg_tito import RCG_TITO_API

_SupporterDict = TypedDict('Supporter', {'first_name': str,
                                         'last_name': str,
                                         'email': str,
                                         'event date': date})


class SupporterCRMExporter():
    """
    The class is used to extract the contact data for previous guests at events
    """

    def __init__(self):

        # make the tito connection
        self.__tito = RCG_TITO_API()

    @property
    def __past_and_archived_events(self):
        return chain(self.__tito.archived_events.items(),
                     self.__tito.past_events.items())


    @property
    def __generate_supporters_data_list(self) -> list[_SupporterDict] :

        supporter_list: list[_SupporterDict] = []
        for event_key, event in self.__past_and_archived_events:
            if event.title == 'Test':
                # skip the test event
                continue
            print(f'{event.title=}')
            for ticket in event.tickets:
                if any([ticket.email is None, ticket.first_name is None, ticket.last_name is None]):
                    # skip any incomplete data records
                    continue
                supporter_list.append({'first_name':ticket.first_name.title(),
                                       'last_name': ticket.last_name.title(),
                                       'email': ticket.email.lower(),
                                       'event date': event.start_at.date()})

        return supporter_list

    def export(self, file_name: Path):

        supporters_df = pd.DataFrame(self.__generate_supporters_data_list)
        # remove duplicated entries using their email address as a unique key, by first sorting by
        # the event date we ensure that only the last visit is kept
        supporters_df.sort_values(by='event date', inplace=True)
        supporters_df.drop_duplicates(subset='email', keep='last', inplace=True)
        # write out a CSV file without the event date columns as that is not relevant data
        supporters_df.drop(labels='event date', axis='columns').to_csv(file_name)


if __name__ == "__main__":

    pass