'''запуск потокового анализатора из командной строки'''

import argparse
import sys

from streamstats.analysis import analyze_files
from streamstats.errors import CommandLineConfigError, StreamStatsError
from streamstats.report import format_summary_json, write_summary_json


def launch_cli() -> int:
    '''разбирает аргументы, выполняет анализ и выводит отчет'''
    # описываем аргументы, которые можно передать программе
    command_parser = argparse.ArgumentParser(prog='streamstats', description='потоковый анализатор событий из CSV и JSONL')

    command_parser.add_argument('operation', metavar='command', help='команда программы: analyze')

    command_parser.add_argument('input_files', metavar='inputs', nargs='+', help='один или несколько входных файлов')

    command_parser.add_argument('--format', dest='data_format', choices=('csv', 'jsonl'), required=True, help='формат входных файлов: csv или jsonl')

    command_parser.add_argument('--output', dest='report_path', metavar='OUTPUT', help='путь к JSON-отчету, без этого аргумента отчет выводится в терминал')

    command_parser.add_argument('--skip-invalid', dest='skip_bad_records', action='store_true', help='пропускать некорректные записи и выводить предупреждения')

    # получаем значения аргументов из команды пользователя
    launch_options = command_parser.parse_args()

    try:
        # проверяем команду и путь для отчета
        if launch_options.operation != 'analyze':

            raise CommandLineConfigError('неизвестная команда, используй analyze')

        if launch_options.report_path is not None:

            if launch_options.report_path.strip() == '':
                raise CommandLineConfigError('путь для отчета не должен быть пустым')

        # передаем файлы анализатору и получаем статистику
        event_summary = analyze_files(launch_options.input_files, launch_options.data_format, skip_invalid=launch_options.skip_bad_records)

        # выводим отчет в терминал или сохраняем в файл
        if launch_options.report_path is None:
            summary_text = format_summary_json(event_summary)
            print(summary_text)

        else:
            write_summary_json(event_summary, launch_options.report_path)

    except (StreamStatsError, OSError, UnicodeError) as command_error:
        print(f'ошибка: {command_error}', file=sys.stderr)
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(launch_cli())
