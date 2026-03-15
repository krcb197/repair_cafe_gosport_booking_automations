
from collections.abc import Iterator
from typing import Optional

from pathlib import Path

import jinja2 as jj
from faker import Faker

from .rcg_tito import RCG_TITO_API
from .rcg_tito import RCG_Ticket
from pytito.admin import Event

_file_dir = Path(__file__).parent
_template_path = _file_dir / "templates"

class RepairForms():
    """
    The class is used for doing a mail merge on the Repair Cafe Gosport repair form using the
    event booking data from TITO
    """

    def __init__(self, fake_personal_data:bool=False):

        # make the tito connection
        self.__tito = RCG_TITO_API()

        self.__fake_data = fake_personal_data
        if fake_personal_data:
            self.__faker = Faker("en_GB")

        # make the jinja environment
        self.__env = jj.Environment(
            loader=jj.FileSystemLoader( _template_path ),
            autoescape=jj.select_autoescape()
        )

        # find the event to make a summary of
        self.set_event(self.__tito.next_event)

    def set_event(self, selected_event:Event):
        # find the event to make a summary of
        self.__event = selected_event
        self.__event_tickets = [RCG_Ticket.build_from_ticket(ticket) for ticket in
                                self.__event.tickets]

    @property
    def repair_cafe_gosport_tito(self) -> RCG_TITO_API:
        """
        instance of the Repair Cafe Gosport Tito Admin API
        """
        return self.__tito

    @property
    def date(self) -> str:
        """
        Event Date Formated "nicely" as 14th March 2026
        """
        day = self.__event.start_at.day

        if 11 <= day <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        return f"{day}{suffix} {self.__event.start_at.strftime('%B %Y')}"


    @property
    def __ticket_data(self) -> list[dict[str, str]]:
        """
        Iterator with all the ticket data for inclusion in the forms
        """
        def clean_none_with_blank(ticket_data: Optional[str]) -> str:
            if ticket_data is None:
                return ""
            return ticket_data

        ticket_list = []
        for ticket in self.__event_tickets:
            ticket_list.append({"Reference": ticket.reference,
                   "Full Name": ticket.name if not self.__fake_data else self.__faker.name(),
                   "Order Email": ticket.email if not self.__fake_data else self.__faker.email(),
                   "Phone Number": clean_none_with_blank(ticket.phone_number) if not self.__fake_data else self.__faker.phone_number(),
                   "Post Code": clean_none_with_blank(ticket.post_code) if not self.__fake_data else self.__faker.postcode(),
                   "Broken Thing": clean_none_with_blank(ticket.repair_item),
                   "Fault Description": clean_none_with_blank(ticket.repair_fault)})
        return ticket_list

    def stream_out_report(self, target_folder: Path):

        template = self.__env.get_template("repair_form.html.jinja")

        template_context = {'event': self.__event,
                            'date': self.date,
                            'tickets': self.__ticket_data}

        output_path = target_folder / 'repair_forms.html'

        with output_path.open('w', encoding='utf-8') as fp:
            stream = template.stream(template_context)
            stream.dump(fp)



if __name__ == "__main__":

    pass