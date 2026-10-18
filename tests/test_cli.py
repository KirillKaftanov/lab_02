import json
import subprocess
import sys


def test_cli_report(tmp_path):
    path1 = tmp_path / 'first.csv'
    path2 = tmp_path / 'second.csv'
    report_path = tmp_path / 'report.json'

    with open(path1, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T13:00:00Z,ERROR,server,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,INFO,приложение,Запуск\n')

    with open(path2, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T14:00:00Z,CRITICAL,server,Сбой\n')

    result = subprocess.run(
        [
            sys.executable, '-m', 'streamstats', 'analyze',
            str(path1), str(path2),
            '--format', 'csv',
            '--output', str(report_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0

    with open(report_path, encoding='utf-8') as file:
        report = json.load(file)

    assert report['total_events'] == 3
    assert report['events_by_level'] == {'DEBUG': 0, 'INFO': 1, 'WARNING': 0, 'ERROR': 1, 'CRITICAL': 1}
    assert report['events_by_source'] == {'server': 2, 'приложение': 1}
    assert report['top_error_sources'] == [{'source': 'server', 'count': 2}]
    assert report['first_timestamp'] == '2026-10-14T12:00:00+00:00'
    assert report['last_timestamp'] == '2026-10-14T14:00:00+00:00'
    assert report['skipped_lines'] == 0


def test_cli_invalid_line(tmp_path):
    path = tmp_path / 'events.csv'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,app,Запуск\n')
        file.write('неверная строка\n')
        file.write('2026-10-14T13:00:00Z,ERROR,server,Ошибка\n')

    result = subprocess.run(
        [
            sys.executable, '-m', 'streamstats', 'analyze',
            str(path), '--format', 'csv',
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert str(path) in result.stderr
    assert 'строка 3' in result.stderr


def test_cli_skip_invalid(tmp_path):
    path = tmp_path / 'events.jsonl'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('{"timestamp": "2026-10-14T12:00:00Z", "level": "INFO", ')
        file.write('"source": "приложение", "message": "Запуск"}\n')
        file.write('не JSON\n')
        file.write('{"timestamp": "2026-10-14T13:00:00Z", "level": "ERROR", ')
        file.write('"source": "server", "message": "Ошибка"}\n')

    result = subprocess.run(
        [
            sys.executable, '-m', 'streamstats', 'analyze',
            str(path), '--format', 'jsonl', '--skip-invalid',
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0

    report = json.loads(result.stdout)

    assert report['total_events'] == 2
    assert report['skipped_lines'] == 1
    assert report['events_by_level']['INFO'] == 1
    assert report['events_by_level']['ERROR'] == 1
    assert report['events_by_source'] == {'приложение': 1, 'server': 1}
    assert 'WARNING' in result.stderr
    assert str(path) in result.stderr
    assert 'строка 2' in result.stderr
