
import pytest

from pytito.admin import Event

from py_rcg_booking_automation import RCG_TITO_API

repair_cafe_gosport_tito = RCG_TITO_API()

def pytest_addoption(parser):
    parser.addoption('--include_draft',
                     action='store_true',
                     help="Include Draft events as well as live events"
    )

@pytest.fixture(scope='session', name='future_events', params=repair_cafe_gosport_tito.events.values(),
                ids=[ event.title.replace("é", "e") for event in repair_cafe_gosport_tito.events.values() ])
def future_events_implementation(request):
    """
    Serve up all the upcoming events as a fixture
    """
    include_draft_events = request.config.getoption("--include_draft")
    event = request.param
    if not isinstance(event, Event):
        raise TypeError(f'expected a {Event} got {type(event)}')
    if event.live:
        yield event
    else:
        if include_draft_events:
            yield event
        else:
            pytest.skip('Skipping Draft event')

@pytest.fixture(scope='session', name='next_event')
def next_event_implementation():
    yield repair_cafe_gosport_tito.next_event