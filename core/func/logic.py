"""
Логические функции.
"""
from datetime import datetime

from .base import LogicFunc, NonMandatoryArg, MandatoryArg


class BoolTrue(LogicFunc):
    """
    Функция, возвращающая логическое True.
    """
    description = 'Функция, возвращающая True'

    @classmethod
    def get_name(cls):
        return 'true'

    def _operation(self, *args):
        return True


class BoolFalse(LogicFunc):
    """
    Функция, возвращающая логическое False.
    """
    description = 'Функция, возвращающая False'

    @classmethod
    def get_name(cls):
        return 'false'

    def _operation(self, *args):
        return False


class Eq(LogicFunc):
    """
    Функция проверки равенства.
    """
    description = 'Проверка равенства двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [str, int, float, bool, datetime, list]),
        MandatoryArg('Значение2', 1, [str, int, float, bool, datetime, list]),
    ]

    def _operation(self, *args):
        return args[0] == args[1]


class Neq(LogicFunc):
    """
    Функция проверки неравенства.
    """
    description = 'Проверка неравенства двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [str, int, float, bool, datetime, list]),
        MandatoryArg('Значение2', 1, [str, int, float, bool, datetime, list]),
    ]

    def _operation(self, *args):
        return args[0] != args[1]


class Gt(LogicFunc):
    """
    Функция проверки x > y.
    """
    description = 'Сравнение Значение1 > Значение2'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float, bool, datetime]),
        MandatoryArg('Значение2', 1, [int, float, bool, datetime]),
    ]

    def _operation(self, *args):
        return args[0] > args[1]


class Gte(LogicFunc):
    """
    Функция проверки x >= y.
    """
    description = 'Сравнение Значение1 >= Значение2'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float, bool, datetime]),
        MandatoryArg('Значение2', 1, [int, float, bool, datetime]),
    ]

    def _operation(self, *args):
        return args[0] >= args[1]


class Lt(LogicFunc):
    """
    Функция проверки x < y.
    """
    description = 'Сравнение Значение1 < Значение2'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float, bool, datetime]),
        MandatoryArg('Значение2', 1, [int, float, bool, datetime]),
    ]

    def _operation(self, *args):
        return args[0] < args[1]


class Lte(LogicFunc):
    """
    Функция проверки x <= y.
    """
    description = 'Сравнение Значение1 <= Значение2'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float, bool, datetime]),
        MandatoryArg('Значение2', 1, [int, float, bool, datetime]),
    ]

    def _operation(self, *args):
        return args[0] <= args[1]


class If(LogicFunc):
    """
    Функция условия.
    """
    description = 'Функция условия IF'
    args_description = [
        MandatoryArg('Условие', 0),
        MandatoryArg('Значение при true', 1),
        MandatoryArg('Значение при false', 2),
    ]

    def _operation(self, *args):
        if args[0] == True:
            return args[1]
        return args[2]


class And(LogicFunc):
    """
    Функция логического умножения AND.
    """
    _arguments_type = bool
    description = 'Функция логического умножения AND'
    args_description = [
        MandatoryArg('Выражение1', 0),
        MandatoryArg('Выражение2', 1),
    ]

    def _operation(self, *args):
        return args[0] & args[1]


class Or(LogicFunc):
    """
    Функция логического сложения OR.
    """
    _arguments_type = bool
    description = 'Функция логического сложения OR'
    args_description = [
        MandatoryArg('Выражение1', 0),
        MandatoryArg('Выражение2', 1),
    ]

    def _operation(self, *args):
        return args[0] | args[1]


class In(LogicFunc):
    """
    Функция проверки вхождения значения в последовательность.
    """
    description = 'Функция проверки вхождения значения в последовательность'
    args_description = [
        MandatoryArg('Значение', 0),
        MandatoryArg('Последовательность', 1, [str, list]),
    ]

    def _operation(self, *args):
        return args[0] in args[1]


class Switch(LogicFunc):
    """
    Функция сравнения с несколькими вариантами.
    """
    description = 'Функция сравнения с несколькими вариантами'
    args_description = [
        MandatoryArg('Значение', 0),
        MandatoryArg('Результат по умолчанию', 1),
        NonMandatoryArg('Список с парой значение-результат', 2),
    ]

    def _operation(self, *args):
        value, default = args[0], args[1]
        cases = args[2:]
        if not cases:
            return default
        cases = {c[0]:c[1] for c in cases}
        try:
            result = cases[value]
        except KeyError:
            result = default
        return result
