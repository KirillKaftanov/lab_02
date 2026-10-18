'''исключения потокового анализатора событий'''


class StreamStatsError(Exception):
    '''базовая ошибка анализатора'''


class CommandLineConfigError(StreamStatsError):
    '''некорректная конфигурация командной строки'''


class EventDataError(StreamStatsError):
    '''некорректная запись события'''


class EventTimestampError(EventDataError):
    '''некорректная временная метка события'''


class InputFormatError(StreamStatsError):
    '''неподдерживаемый формат входных данных'''
