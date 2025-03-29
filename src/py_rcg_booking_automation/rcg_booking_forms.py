
from .rcg_tito import RCG_TITO_API
from .rcg_tito import RCG_Ticket

from .google_apps import GoogleDoc, GoogleDrive, google_credentials

class EventBookingForms():
    """
    The class is used for doing a mail merge on the Repair Cafe Gosport repair form using the
    event booking data from TITO
    """
    TEMPLATE_ID = "1eeqf94Q2_dNJm0PPEga6cwwrjhlWma6r3AkxOgG_aTE"
    BOOKING_FOLDER_ID = "1UvXsVDeYHrtZl6ZZ2rD8iRdczhIhJt_X"

    SCOPES = GoogleDoc.SCOPES + GoogleDrive.SCOPES

    def __init__(self):

        # make the tito connection
        self.__tito = RCG_TITO_API()

        # find the event to make a summary of
        self.__event = self.__tito.next_event
        self.__event_tickets = [RCG_Ticket.build_from_ticket(ticket) for ticket in
                                self.__event.tickets]

        # make a google docs connection
        self.__creds = google_credentials(self.SCOPES)
        self.doc_api = GoogleDoc(self.__creds)
        self.drive_api = GoogleDrive(self.__creds)
        # self.__template_form = self.doc_api.get_document(self.TEMPLATE_ID)
        # print(f"The title of the document is: {self.__template_form.get('title')}")

        self.__event_folder_id = \
            self.drive_api.create_folder(self.drive_folder_name,
                                         self.BOOKING_FOLDER_ID)

        self.__individual_forms = {}
        self.make_individual_forms()

        self.merge_individual_forms()


    @property
    def drive_folder_name(self):
        return self.__event._event_slug.replace('-', '_')

    def make_individual_forms(self):
        """
        For each event booking:
        1. Copy the template to a new file
        2. Replace all the booking data with the event data
        """

        for ticket in self.__event_tickets[0:2]:
            filename = f"{self.__event._event_slug.replace('-', '_')}_{ticket.reference.replace('-', '_')}"

            self.__individual_forms[ticket.reference] = self.drive_api.copy_file(file_id=self.TEMPLATE_ID,
                                                                                 new_name=filename,
                                                                                 target_folder_id=self.__event_folder_id)
            print(f'Created File ID: "{self.__individual_forms[ticket.reference]}".')

            merge_data = {"Ticket Reference": ticket.reference,
                          "Ticket": "time",
                          "EventDate": "8th March 2025",
                          "Ticket Full Name": ticket.name,
                          "Order Email": ticket.email}
            if ticket.phone_number is not None:
                merge_data["Phone Number"] = ticket.phone_number
            else:
                merge_data["Phone Number"] = ""

            if ticket.post_code is not None:
                merge_data["Post Code"] = ticket.post_code
            else:
                merge_data["Post Code"] = ""

            if ticket.repair_item is not None:
                merge_data["Description of the Broken Things"] = ticket.repair_item
            else:
                merge_data["Description of the Broken Things"] = ""

            if ticket.repair_fault is not None:
                merge_data["Description of the Fault"] = ticket.repair_fault
            else:
                merge_data["Description of the Fault"] = ""

            if ticket.repair_type is not None:
                merge_data["What type of Broken Thing do you want help with"] = ticket.repair_type
            else:
                merge_data["What type of Broken Thing do you want help with"] = ""

            self.doc_api.update_strings(document_id=self.__individual_forms[ticket.reference],
                                        updates=merge_data)

    def merge_individual_forms(self):
        """
        merge the individual google docs into a single doc
        """
        self.doc_api.merge_google_docs(doc_ids=[item for item in self.__individual_forms.values()],
                                       new_doc_title="March 2025 Merged Bookings")

if __name__ == "__main__":

    pass