'''проверка данных и создание события'''

from datetime import datetime, timezone

from .errors import EventDataError, EventTimestampError


def prepare_event(record_data: object) -> dict[str, str | datetime]:
    if not isinstance(record_data, dict):
        raise EventDataError('запись события должна быть словарем')

    required_fields = ('timestamp', 'level', 'source', 'message')
    allowed_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    for field_name in required_fields:
        if field_name not in record_data:
            raise EventDataError(f'отсутствует поле: {field_name}')

    for field_name in required_fields:
        field_value = record_data[field_name]

        if not isinstance(field_value, str):
            error_text = f'поле {field_name} должно быть строкой'
            if field_name == 'timestamp':
                raise EventTimestampError(error_text)
            raise EventDataError(error_text)

        if field_name == 'timestamp':
            if field_value.strip() == '':
                raise EventTimestampError('поле timestamp не должно быть пустым')
            if 'T' not in field_value:
                raise EventTimestampError('в timestamp нужны дата и время через T')

        elif field_name == 'level':
            if field_value not in allowed_levels:
                raise EventDataError('неизвестный уровень события')

        elif field_name == 'source':
            if field_value.strip() == '':
                raise EventDataError('поле source не должно быть пустым')

    time_text = record_data['timestamp']
    time_part = time_text.split('T', 1)[1]

    for sign in ('+', '-'):
        if sign in time_part:
            offset_text = time_part.split(sign, 1)[1]
            offset_digits = offset_text.replace(':', '')

            if len(offset_digits) not in (2, 4) or not offset_digits.isdecimal():
                raise EventTimestampError('неверный часовой пояс')

            offset_hours = int(offset_digits[:2])
            offset_minutes = 0

            if len(offset_digits) == 4:
                offset_minutes = int(offset_digits[2:])

            if offset_hours > 23 or offset_minutes > 59:
                raise EventTimestampError('неверный часовой пояс')

    try:
        parsed_time = datetime.fromisoformat(time_text.replace('Z', '+00:00'))

        if parsed_time.tzinfo is None:
            parsed_time = parsed_time.replace(tzinfo=timezone.utc)

        utc_time = parsed_time.astimezone(timezone.utc)

    except (ValueError, OverflowError) as conversion_error:
        raise EventTimestampError('неверная временная метка') from conversion_error

    return {'timestamp': utc_time, 'level': record_data['level'], 'source': record_data['source'], 'message': record_data['message']}
