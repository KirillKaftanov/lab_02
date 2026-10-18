'''формирование и сохранение JSON-отчета'''

import json


def format_summary_json(summary: dict) -> str:
    '''преобразовать статистику в текст JSON-отчета'''
    report_fields = {}

    field_names = [
        'total_events',
        'events_by_level',
        'events_by_source',
        'top_error_sources',
        'first_timestamp',
        'last_timestamp',
        'skipped_lines',
    ]

    for field_name in field_names:
        report_fields[field_name] = summary[field_name]

    for field_name in ['first_timestamp', 'last_timestamp']:
        recorded_at = report_fields[field_name]

        if recorded_at is not None:
            report_fields[field_name] = recorded_at.isoformat()

    encoded_report = json.dumps(report_fields, ensure_ascii=False, indent=4)

    return encoded_report


def write_summary_json(summary: dict, output_path: str) -> None:
    '''сохранить JSON-отчет в файл'''
    encoded_report = format_summary_json(summary)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(encoded_report + '\n')
