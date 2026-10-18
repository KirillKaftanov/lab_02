import pytest
from streamstats.errors import EventDataError
from streamstats.parsers import read_csv_events, read_jsonl_events


def test_parse_csv(tmp_path):
    path = tmp_path / 'events.csv'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,приложение,Привет\n')

    events = list(read_csv_events(path))

    assert len(events) == 1
    assert events[0]['timestamp'].isoformat() == '2026-10-14T12:00:00+00:00'
    assert events[0]['level'] == 'INFO'
    assert events[0]['source'] == 'приложение'
    assert events[0]['message'] == 'Привет'


def test_parse_jsonl(tmp_path):
    path = tmp_path / 'events.jsonl'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('{"timestamp": "2026-10-14T12:00:00Z", "level": "INFO", ')
        file.write('"source": "приложение", "message": "Привет"}\n')

    events = list(read_jsonl_events(path))

    assert len(events) == 1
    assert events[0]['timestamp'].isoformat() == '2026-10-14T12:00:00+00:00'
    assert events[0]['level'] == 'INFO'
    assert events[0]['source'] == 'приложение'
    assert events[0]['message'] == 'Привет'


def test_empty_files(tmp_path):
    csv_path = tmp_path / 'empty.csv'
    jsonl_path = tmp_path / 'empty.jsonl'

    with open(csv_path, 'w', encoding='utf-8') as file:
        file.write('')

    with open(jsonl_path, 'w', encoding='utf-8') as file:
        file.write('')

    assert list(read_csv_events(csv_path)) == []
    assert list(read_jsonl_events(jsonl_path)) == []


def test_csv_invalid_line(tmp_path):
    path = tmp_path / 'events.csv'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,app,Запуск\n')
        file.write('неверная строка\n')
        file.write('2026-10-14T13:00:00Z,ERROR,server,Ошибка\n')

    with pytest.raises(EventDataError) as error:
        list(read_csv_events(path))

    assert str(path) in str(error.value)
    assert 'строка 3' in str(error.value)


def test_jsonl_invalid_line(tmp_path):
    path = tmp_path / 'events.jsonl'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('{"timestamp": "2026-10-14T12:00:00Z", "level": "INFO", ')
        file.write('"source": "app", "message": "Запуск"}\n')
        file.write('не JSON\n')
        file.write('{"timestamp": "2026-10-14T13:00:00Z", "level": "ERROR", ')
        file.write('"source": "server", "message": "Ошибка"}\n')

    with pytest.raises(EventDataError) as error:
        list(read_jsonl_events(path))

    assert str(path) in str(error.value)
    assert 'строка 2' in str(error.value)


def test_csv_skip_invalid(tmp_path, caplog):
    path = tmp_path / 'events.csv'
    stats = {'skipped_lines': 0}

    with open(path, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,app,Запуск\n')
        file.write('неверная строка\n')
        file.write('2026-10-14T13:00:00Z,ERROR,server,Ошибка\n')

    events = list(read_csv_events(path, ignore_bad_records=True, skip_totals=stats))

    assert len(events) == 2
    assert events[0]['level'] == 'INFO'
    assert events[1]['level'] == 'ERROR'
    assert stats['skipped_lines'] == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'WARNING'
    assert str(path) in caplog.text
    assert 'строка 3' in caplog.text


def test_jsonl_skip_invalid(tmp_path, caplog):
    path = tmp_path / 'events.jsonl'
    stats = {'skipped_lines': 0}

    with open(path, 'w', encoding='utf-8') as file:
        file.write('{"timestamp": "2026-10-14T12:00:00Z", "level": "INFO", ')
        file.write('"source": "app", "message": "Запуск"}\n')
        file.write('не JSON\n')
        file.write('{"timestamp": "2026-10-14T13:00:00Z", "level": "ERROR", ')
        file.write('"source": "server", "message": "Ошибка"}\n')

    events = list(read_jsonl_events(path, ignore_bad_records=True, skip_totals=stats))

    assert len(events) == 2
    assert events[0]['level'] == 'INFO'
    assert events[1]['level'] == 'ERROR'
    assert stats['skipped_lines'] == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'WARNING'
    assert str(path) in caplog.text
    assert 'строка 2' in caplog.text
