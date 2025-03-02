
from pathlib import Path

from py_rcg_booking_automation import EventSummaryReport

file_path = Path(__file__).parent

if __name__ == '__main__':

    # this is the ID of the event_summary_reports folder in the chair google drive where the
    # images directory for the event will be stored
    event_summary_report_folder_id = "1cmDkAELqxMZ8ZjSmExipVd18Pmpbrdxc"

    event_report = EventSummaryReport(event_summary_report_folder_id)
    # this will create a file called 'booking.html' in the HTML output directory
    event_report.stream_out_report(file_path / 'html_output')

    print('Now makes the new folder publically viewble so everyone can see it')


