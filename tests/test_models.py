import pytest

from streamstats.errors import EventTimestampError
from streamstats.models import prepare_event


def test_invalid_timezone():
    event_data = {
        'timestamp': '2026-10-18T12:00:00+03:99',
        'level': 'INFO',
        'source': 'app',
        'message': 'Запуск',
    }

    with pytest.raises(EventTimestampError):
        prepare_event(event_data)
