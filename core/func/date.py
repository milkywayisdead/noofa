"""
Функции работы с датой и временем.
"""

from datetime import datetime

from .base import DateFunc, NonMandatoryArg, MandatoryArg


_DEFAULT_FMT = '%d-%m-%Y %H:%M:%S'


def _seconds_to_datetimestr(seconds, fmt):
    return datetime.fromtimestamp(seconds).strftime(fmt)


class SecToDate(DateFunc):
    """
    Перевод секунд в дату и время.
    """
    description = 'Перевод секунд в дату и время'
    args_description = [
        MandatoryArg('Секунды', 0),
        NonMandatoryArg('Формат', 1),
    ]

    def _operation(self, *args):
        seconds = args[0]
        try:
            fmt = args[1]
        except IndexError:
            fmt = _DEFAULT_FMT
        return _seconds_to_datetimestr(seconds, fmt)


class MsecToDate(DateFunc):
    """
    Перевод миллисекунд в дату и время.
    """
    description = 'Перевод миллисекунд в дату и время'
    args_description = [
        MandatoryArg('Секунды', 0),
        NonMandatoryArg('Формат', 1),
    ]

    def _operation(self, *args):
        seconds = args[0]
        try:
            fmt = args[1]
        except IndexError:
            fmt = _DEFAULT_FMT
        return _seconds_to_datetimestr(seconds/1000, fmt)


class Now(DateFunc):
    """
    Получение текущей даты и времени.
    """
    description = 'Получение текущей даты и времени'