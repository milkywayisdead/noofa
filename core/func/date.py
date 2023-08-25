"""
Функции работы с датой и временем.
"""

from datetime import datetime, date, time

from .base import DateFunc, NonMandatoryArg, MandatoryArg


_DEFAULT_FMT = '%Y-%m-%d %H:%M:%S'
_DEFAULT_TIME_FMT = '%H:%M:%S'
_DEFAULT_DATE_FMT = '%Y-%m-%d'

_DEFAULT_FMTS = {
    time: _DEFAULT_TIME_FMT,
    date: _DEFAULT_DATE_FMT,
    datetime: _DEFAULT_FMT,
}


def _seconds_to_datetimestr(seconds, fmt):
    return datetime.fromtimestamp(seconds).strftime(fmt)


class SecToDate(DateFunc):
    """
    Перевод секунд в дату и время.
    """
    description = 'Перевод секунд в дату и время'
    args_description = [
        MandatoryArg('Секунды', 0, [int, float]),
    ]

    def _operation(self, *args):
        seconds = args[0]
        return datetime.fromtimestamp(seconds)


class MsecToDate(DateFunc):
    """
    Перевод миллисекунд в дату и время.
    """
    description = 'Перевод миллисекунд в дату и время'
    args_description = [
        MandatoryArg('Миллисекунды', 0, [int, float]),
    ]

    def _operation(self, *args):
        msec = args[0]
        return datetime.fromtimestamp(msec/1000)


class SecToDateStr(DateFunc):
    """
    Перевод секунд в строку даты и времени.
    """
    description = 'Перевод секунд в строку даты и времени'
    args_description = [
        MandatoryArg('Секунды', 0, [int, float]),
        NonMandatoryArg('Формат', 1, [str]),
    ]

    def _operation(self, *args):
        seconds = args[0]
        try:
            fmt = args[1]
        except IndexError:
            fmt = _DEFAULT_FMT
        return _seconds_to_datetimestr(seconds, fmt)


class MsecToDateStr(DateFunc):
    """
    Перевод миллисекунд в строку даты и времени.
    """
    description = 'Перевод миллисекунд в строку даты и времени'
    args_description = [
        MandatoryArg('Миллисекунды', 0, [int, float]),
        NonMandatoryArg('Формат', 1, [str]),
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
    args_description = []

    def _operation(self, *args):
        return datetime.now()


class Date(DateFunc):
    """
    Получение текущей даты.
    """
    description = 'Получение текущей даты'
    args_description = []

    def _operation(self, *args):
        return datetime.now().date()


class Time(DateFunc):
    """
    Получение текущего времени.
    """
    description = 'Получение текущего времени'
    args_description = []

    def _operation(self, *args):
        return datetime.now().time()


class DateToSec(DateFunc):
    """
    Перевод даты в секунды.
    """
    description = 'Перевод даты в секунды'
    args_description = [
        MandatoryArg('Дата', 0, [datetime]),
    ]

    def _operation(self, *args):
        return int(args[0].timestamp())


class DateToStr(DateFunc):
    """
    Перевод даты/времени в строку.
    """
    description = 'Перевод даты/времени в строку'
    args_description = [
        MandatoryArg('Дата', 0, [datetime, date, time]),
        NonMandatoryArg('Формат', 1, [str]),
    ]

    def _operation(self, *args):
        dt = args[0]
        try:
            fmt = args[1]
        except IndexError:
            fmt = _DEFAULT_FMTS.get(type(dt), _DEFAULT_FMT)
        return dt.strftime(fmt)


class StrToDate(DateFunc):
    """
    Перевод строки в дату/время.
    """
    description = 'Перевод строки в дату/время'
    args_description = [
        MandatoryArg('Строка', 0, [str]),
        NonMandatoryArg('Формат', 1, [str]),
    ]

    def _operation(self, *args):
        dt = args[0]
        try:
            fmt = args[1]
        except IndexError:
            fmt = _DEFAULT_FMT
        return datetime.strptime(dt, fmt)
