"""
script to generate a new repair cafe gosport event
"""
from datetime import time, timezone
from py_rcg_booking_automation import RCG_TITO_API

if __name__ == '__main__':

    repair_cafe_gosport_tito = RCG_TITO_API()
    for event_slug, event in repair_cafe_gosport_tito.archived_events.items():
        # ticket types are known as releases
        for release_slug, release in event.releases.items():
            if release.end_at is None:
                release.end_at = event.start_at
                print(f'{event.title} - Updating {release.title} end_at')

