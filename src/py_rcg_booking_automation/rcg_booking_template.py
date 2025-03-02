

import os.path

from py_rcg_booking_automation import RCG_TITO_API, RCG_Ticket







if __name__ == "__main__":

    tito = RCG_TITO_API()
    # next_event = tito.past_events['repair-cafe-december-2024']
    next_event = tito.next_event
    next_event_tickets = [RCG_Ticket.build_from_ticket(ticket) for ticket in next_event.tickets]

    doc_processor = GoogleDoc()