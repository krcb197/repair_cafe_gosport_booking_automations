"""
script to generate a new repair cafe gosport event
"""
from datetime import time, timezone
from py_rcg_booking_automation import RCG_TITO_API

if __name__ == '__main__':

    repair_cafe_gosport_tito = RCG_TITO_API()
    new_event_def = repair_cafe_gosport_tito.new_event(
         month=3, year=2026,
         start_time=time(hour=10, minute=30, tzinfo=timezone.utc))

    secret_settings = new_event_def._get_response('settings/tickets')['event']
    print(secret_settings['ticket_success_message'])
    print(secret_settings['custom_registration_unavailable_message'])

