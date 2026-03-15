"""
script to generate a new repair cafe gosport event booking forms by merging data from the
booking system with the template
"""
from pathlib import Path

from py_rcg_booking_automation import RepairForms

file_path = Path(__file__).parent

if __name__ == '__main__':
    repair_forms = RepairForms(fake_personal_data=True)

    # for testing for this to March 2026 (which has lots of data)
    repair_forms.set_event(selected_event=repair_forms.repair_cafe_gosport_tito.past_events['repair-cafe-march-2026'])

    # this will create a file called 'booking.html' in the HTML output directory
    repair_forms.stream_out_report(file_path / 'html_output')