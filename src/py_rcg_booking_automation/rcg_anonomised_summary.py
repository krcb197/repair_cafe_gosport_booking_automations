"""
The module provides an anonymised report of all the items booked into a Repair Cafe Gosport
Event
"""
from tempfile import TemporaryDirectory
from pathlib import Path
from dataclasses import dataclass

import jinja2 as jj
from PIL import Image

from .rcg_tito import RCG_TITO_API
from .rcg_tito import RCG_Ticket
from .google_apps import GoogleDrive

file_dir = Path(__file__).parent
template_path = file_dir / "templates"

@dataclass
class _UploadedGooglePicture:
    filename : str
    google_drive_file_id: str

class EventSummaryReport():

    def __init__(self, root_folder_id):

        # make the tito connection
        self.__tito = RCG_TITO_API()

        # find the event to make a summary of
        self.__event = self.__tito.next_event

        # make a google drive connection
        self.drive_api = GoogleDrive()
        self.__root_folder_id = root_folder_id
        self.create_event_folder()

        # make the jinja enviroment
        self.__env = jj.Environment(
            loader=jj.FileSystemLoader( template_path ),
            autoescape=jj.select_autoescape()
        )

        # retrieve tito event data
        self.ingest_event_data()

    @property
    def drive_folder_name(self):
        return self.__event._event_slug.replace('-', '_')

    def create_event_folder(self):
        self.__event_picture_folder_id = \
            self.drive_api.create_folder(self.drive_folder_name,
                                         self.__root_folder_id)

    def ingest_event_data(self):

        self.__event_tickets = [RCG_Ticket.build_from_ticket(ticket) for ticket in
                                self.__event.tickets]

        self.__ticket_pictures = {}
        with TemporaryDirectory() as tempdir:
            temp_path = Path(tempdir)
            for ticket in self.__event_tickets:
                if ticket.repair_picture_present:
                    print(f'retrieving:{ticket.reference}')
                    cleaned_reference = ticket.reference.replace('-', '_')
                    filename_full = cleaned_reference + '_full_quality.JPG'
                    filename = cleaned_reference + '.JPG'

                    fq_temp_pic = temp_path / filename_full
                    fq_output_pic = temp_path / filename

                    ticket.retrieve_repair_picture(fq_temp_pic)

                    # process the picture to make it 1024 wide and lower quality
                    with Image.open(fq_temp_pic) as im:
                        im.thumbnail((1024, 1024))
                        im.save(fq_output_pic, quality=50)

                    upload_id = self.drive_api.upload_file(fq_output_pic,
                                                           self.__event_picture_folder_id)

                    self.__ticket_pictures[ticket.reference] = \
                        _UploadedGooglePicture(filename=filename,
                                               google_drive_file_id=upload_id)
                else:
                    self.__ticket_pictures[ticket.reference] = None


    def stream_out_report(self, target_folder: Path):

        template = self.__env.get_template("booking_volunteer_summary.html.jinja")

        template_context = {'event': self.__event,
                            'tickets': self.__event_tickets,
                            'ticket_pictures': self.__ticket_pictures}

        output_path = target_folder / 'bookings.html'

        with output_path.open('w', encoding='utf-8') as fp:
            stream = template.stream(template_context)
            stream.dump(fp)

if __name__ == '__main__':

    pass