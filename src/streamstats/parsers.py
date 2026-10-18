'''построчное чтение событий из CSV и JSONL'''

import sys
import csv
import json
import logging
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from .errors import EventDataError, EventTimestampError, InputFormatError
from .models import prepare_event


def process_record_error(input_path: str | Path, record_line: int, read_error: Exception, ignore_bad_records: bool, skip_totals: dict[str, int] | None) -> None:
    '''останавливает обработку или берет в учет пропущенную запись'''
    diagnostic_text = f'файл "{input_path}", строка {record_line}: {read_error}'

    if ignore_bad_records:

        if skip_totals is not None:

            if 'skipped_lines' in skip_totals:
                skip_totals['skipped_lines'] = skip_totals['skipped_lines'] + 1

            else:
                skip_totals['skipped_lines'] = 1

        logging.warning(diagnostic_text)
        return

    if isinstance(read_error, EventTimestampError):
        raise EventTimestampError(diagnostic_text) from read_error

    raise EventDataError(diagnostic_text) from read_error


def read_jsonl_events(input_path: str | Path, ignore_bad_records: bool = False, skip_totals: dict[str, int] | None = None) -> Iterator[dict[str, str | datetime]]:
    '''выдает проверенные события из JSONL по одному'''
    with open(input_path, encoding='utf-8-sig') as input_stream:

        record_line = 0

        for json_text in input_stream:

            record_line = record_line + 1

            try:
                record_values = json.loads(json_text)
                checked_event = prepare_event(record_values)

            except (json.JSONDecodeError, EventDataError) as read_error:
                process_record_error(input_path, record_line, read_error, ignore_bad_records, skip_totals)
                continue

            yield checked_event


def read_csv_events(input_path: str | Path, ignore_bad_records: bool = False, skip_totals: dict[str, int] | None = None) -> Iterator[dict[str, str | datetime]]:
    '''выдает проверенные события из CSV с заголовком по одному'''
    with open(input_path, encoding='utf-8-sig', newline='') as input_stream:
        csv.field_size_limit(sys.maxsize)
        csv_rows = csv.reader(input_stream, strict=True)

        try:
            column_names = next(csv_rows)

        except StopIteration:
            return

        except csv.Error as read_error:
            raise EventDataError(f'файл "{input_path}", строка 1: неверный CSV-заголовок: {read_error}') from read_error

        for column_name in column_names:

            if column_names.count(column_name) > 1:
                raise EventDataError(f'файл "{input_path}", строка 1: повторяется столбец {column_name}')

        for required_name in ('timestamp', 'level', 'source', 'message'):

            if required_name not in column_names:
                raise EventDataError(f'файл "{input_path}", строка 1: в заголовке нет поля {required_name}')

        while True:
            record_line = csv_rows.line_num + 1

            try:
                cell_values = next(csv_rows)

            except StopIteration:
                break

            except csv.Error as read_error:
                process_record_error(input_path, record_line, read_error, ignore_bad_records, skip_totals)
                continue

            try:

                if len(cell_values) != len(column_names):
                    raise EventDataError('количество значений не совпадает с числом столбцов')

                record_values = {}

                column_index = 0

                while column_index < len(column_names):

                    column_name = column_names[column_index]
                    cell_value = cell_values[column_index]
                    record_values[column_name] = cell_value

                    column_index = column_index + 1

                checked_event = prepare_event(record_values)

            except EventDataError as read_error:
                process_record_error(input_path, record_line, read_error, ignore_bad_records, skip_totals)
                continue

            yield checked_event


def read_event_stream(input_path: str | Path, input_format: str, ignore_bad_records: bool = False, skip_totals: dict[str, int] | None = None) -> Iterator[dict[str, str | datetime]]:
    '''выбирает парсер по указанному формату'''
    if input_format == 'jsonl':
        return read_jsonl_events(input_path, ignore_bad_records, skip_totals)

    if input_format == 'csv':
        return read_csv_events(input_path, ignore_bad_records, skip_totals)

    raise InputFormatError(f'неподдерживаемый формат: {input_format}')
