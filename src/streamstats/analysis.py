'''подсчёт статистики событий из входных файлов'''

from datetime import datetime
from typing import cast

from streamstats.parsers import read_event_stream


def analyze_files(paths: list, file_format: str, skip_invalid: bool = False) -> dict:
    '''собирает общую статистику по всем переданным файлам'''
    event_count = 0
    level_counts = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
    source_counts: dict[str, int] = {}
    failure_counts: dict[str, int] = {}

    earliest_time: datetime | None = None
    latest_time: datetime | None = None
    parse_counts = {'skipped_lines': 0}

    for input_path in paths:
        records = read_event_stream(input_path, file_format, ignore_bad_records=skip_invalid, skip_totals=parse_counts)

        for record in records:
            event_count = event_count + 1
            severity = cast(str, record['level'])
            origin = cast(str, record['source'])
            recorded_at = cast(datetime, record['timestamp'])

            level_counts[severity] = level_counts[severity] + 1

            if origin in source_counts:
                source_counts[origin] = source_counts[origin] + 1
            else:
                source_counts[origin] = 1

            if severity == 'ERROR' or severity == 'CRITICAL':
                if origin in failure_counts:
                    failure_counts[origin] = failure_counts[origin] + 1
                else:
                    failure_counts[origin] = 1

            if earliest_time is None or recorded_at < earliest_time:
                earliest_time = recorded_at

            if latest_time is None or recorded_at > latest_time:
                latest_time = recorded_at

    error_leaders: list[dict[str, str | int]] = []
    remaining_sources = list(failure_counts)

    # на каждом проходе выбираем один источник для следующего места
    while len(remaining_sources) > 0 and len(error_leaders) < 5:
        selected_source = remaining_sources[0]

        for origin in remaining_sources:
            if failure_counts[origin] > failure_counts[selected_source]:
                selected_source = origin

        error_leaders.append({'source': selected_source, 'count': failure_counts[selected_source]})

        remaining_sources.remove(selected_source)

    return {
        'total_events': event_count,
        'events_by_level': level_counts,
        'events_by_source': source_counts,
        'top_error_sources': error_leaders,
        'first_timestamp': earliest_time,
        'last_timestamp': latest_time,
        'skipped_lines': parse_counts['skipped_lines'],
    }
