"""
This module extends the pytito mode to provide specific behaviours for a Repair Cafe Gosport
TITO event
"""

from typing import Any, Optional
from pytito import AdminAPI
from pytito.admin import Account
from pytito.admin import Ticket

import requests

class RCG_Ticket(Ticket):
    """
    Extension to the Ticket Class provided by pyTito with the features of a book at Repair
    Cafe Gosport
    """

    @classmethod
    def build_from_ticket(cls, ticket: Ticket) -> 'RCG_Ticket':
        return cls(account_slug=ticket._account_slug,
                   event_slug=ticket._event_slug,
                   ticket_slug=ticket._ticket_slug)


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




