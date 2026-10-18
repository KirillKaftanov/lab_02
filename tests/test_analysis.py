from streamstats.analysis import analyze_files


def test_statistics(tmp_path):
    path = tmp_path / 'events.csv'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,приложение,Запуск\n')
        file.write('2026-10-14T10:00:00Z,ERROR,server,Ошибка\n')
        file.write('2026-10-14T13:00:00Z,CRITICAL,server,Ошибка\n')
        file.write('2026-10-14T09:00:00Z,DEBUG,приложение,Отладка\n')
        file.write('2026-10-14T11:00:00Z,WARNING,db,Предупреждение\n')
        file.write('2026-10-14T14:00:00Z,ERROR,db,Ошибка\n')
        file.write('2026-10-14T08:00:00Z,INFO,приложение,Запуск\n')

    stats = analyze_files([path], 'csv')

    assert stats['total_events'] == 7
    assert stats['events_by_level'] == {'DEBUG': 1, 'INFO': 2, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 1}
    assert stats['events_by_source'] == {'приложение': 3, 'server': 2, 'db': 2}
    assert stats['top_error_sources'] == [{'source': 'server', 'count': 2}, {'source': 'db', 'count': 1}]
    assert stats['first_timestamp'].isoformat() == '2026-10-14T08:00:00+00:00'
    assert stats['last_timestamp'].isoformat() == '2026-10-14T14:00:00+00:00'
    assert stats['skipped_lines'] == 0


def test_empty_file(tmp_path):
    path = tmp_path / 'empty.csv'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('')

    stats = analyze_files([path], 'csv')

    assert stats['total_events'] == 0
    assert stats['events_by_level'] == {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
    assert stats['events_by_source'] == {}
    assert stats['top_error_sources'] == []
    assert stats['first_timestamp'] is None
    assert stats['last_timestamp'] is None
    assert stats['skipped_lines'] == 0


def test_multiple_files(tmp_path):
    path1 = tmp_path / 'first.csv'
    path2 = tmp_path / 'second.csv'

    with open(path1, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,app,Запуск\n')
        file.write('2026-10-14T10:00:00Z,ERROR,server,Ошибка\n')

    with open(path2, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T15:00:00Z,CRITICAL,server,Ошибка\n')
        file.write('2026-10-14T08:00:00Z,WARNING,db,Предупреждение\n')

    stats = analyze_files([path1, path2], 'csv')

    assert stats['total_events'] == 4
    assert stats['events_by_level'] == {'DEBUG': 0, 'INFO': 1, 'WARNING': 1, 'ERROR': 1, 'CRITICAL': 1}
    assert stats['events_by_source'] == {'app': 1, 'server': 2, 'db': 1}
    assert stats['top_error_sources'] == [{'source': 'server', 'count': 2}]
    assert stats['first_timestamp'].isoformat() == '2026-10-14T08:00:00+00:00'
    assert stats['last_timestamp'].isoformat() == '2026-10-14T15:00:00+00:00'


def test_top_five_sources(tmp_path):
    path = tmp_path / 'errors.csv'

    with open(path, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')

        file.write('2026-10-14T12:00:00Z,ERROR,a,Ошибка\n')

        file.write('2026-10-14T12:00:00Z,ERROR,b,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,b,Ошибка\n')

        file.write('2026-10-14T12:00:00Z,ERROR,c,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,c,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,c,Ошибка\n')

        file.write('2026-10-14T12:00:00Z,ERROR,d,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,d,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,d,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,d,Ошибка\n')

        file.write('2026-10-14T12:00:00Z,ERROR,e,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,e,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,e,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,e,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,e,Ошибка\n')

        file.write('2026-10-14T12:00:00Z,ERROR,f,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,f,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,f,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,f,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,f,Ошибка\n')
        file.write('2026-10-14T12:00:00Z,ERROR,f,Ошибка\n')

    stats = analyze_files([path], 'csv')

    assert stats['total_events'] == 21
    assert stats['top_error_sources'] == [
        {'source': 'f', 'count': 6},
        {'source': 'e', 'count': 5},
        {'source': 'd', 'count': 4},
        {'source': 'c', 'count': 3},
        {'source': 'b', 'count': 2},
    ]


def test_skipped_lines(tmp_path):
    path1 = tmp_path / 'first.csv'
    path2 = tmp_path / 'second.csv'

    with open(path1, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T12:00:00Z,INFO,app,Запуск\n')
        file.write('неверная строка\n')

    with open(path2, 'w', encoding='utf-8') as file:
        file.write('timestamp,level,source,message\n')
        file.write('2026-10-14T13:00:00Z,ERROR,server,Ошибка\n')
        file.write('2026-10-14T14:00:00Z,UNKNOWN,db,Сообщение\n')

    stats = analyze_files([path1, path2], 'csv', skip_invalid=True)

    assert stats['total_events'] == 2
    assert stats['skipped_lines'] == 2
    assert stats['events_by_source'] == {'app': 1, 'server': 1}
    assert stats['events_by_level']['INFO'] == 1
    assert stats['events_by_level']['ERROR'] == 1
    assert stats['top_error_sources'] == [{'source': 'server', 'count': 1}]
