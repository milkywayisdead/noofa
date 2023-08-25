"""
Операторы.
"""
from datetime import datetime

from .base import Operator, MandatoryArg
from ..dataframes import panda_builder


_OPERATORS_PRIORITY = {
    '*': 1,
    '/': 1,
    '+': 2,
    '-': 2,
    '>': 3,
    '<': 3,
    '>=': 3,
    '<=': 3,
    '!=': 4,
    '==': 4,
    '&': 5,
    '|': 6,
}


_NONE_TYPE = type(None)


class Add(Operator):
    """
    Сумма двух чисел.
    """
    sign = '+'
    description = 'Сумма двух чисел или конкатенация строк'
    args_description = [
        MandatoryArg('Число1', 0, [int, float, str, _NONE_TYPE, panda_builder.pd.DataFrame]),
        MandatoryArg('Число2', 1, [int, float, str, panda_builder.pd.DataFrame]),
    ]

    def _operation(self, *args):
        left, right = args
        if isinstance(left, panda_builder.pd.DataFrame) and isinstance(right, panda_builder.pd.DataFrame):
            return panda_builder.union([left, right])
        if left is None and type(right) is not str:
            return right
        return left + right


class Subtract(Operator):
    """
    Вычитание.
    """
    sign = '-'
    description = 'Вычитание'
    args_description = [
        MandatoryArg('Число1', 0, [int, float, str, _NONE_TYPE]),
        MandatoryArg('Число2', 1, [int, float, str]),
    ]

    def _operation(self, *args):
        left, right = args
        if left is None and type(right) is not str:
            left = 0
        return left - right


class Divide(Operator):
    """
    Деление.
    """
    sign = '/'
    description = 'Деление'
    args_description = [
        MandatoryArg('Число1', 0, [int, float]),
        MandatoryArg('Число2', 1, [int, float]),
    ]

    def _operation(self, *args):
        return args[0] / args[1]


class Multiply(Operator):
    """
    Умножение.
    """
    sign = '*'
    description = 'Умножение'
    args_description = [
        MandatoryArg('Число1', 0, [int, float]),
        MandatoryArg('Число2', 1, [int, float]),
    ]

    def _operation(self, *args):
        return args[0] * args[1]


class Assign(Operator):
    """
    Присваивание значения.
    """
    sign = '='
    description = 'Присваивание значения'
    args_description = [
        MandatoryArg('Имя переменной', 0),
        MandatoryArg('Значение', 1),
    ]

    def _operation(self, *args):
        return {args[0]: args[1]}


class IsGt(Operator):
    """
    Сравнение >.
    """
    sign = '>'
    description = 'Сравнение > двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float, bool, datetime]),
        MandatoryArg('Значение2', 1, [int, float, bool, datetime]),
    ]

    def _operation(self, *args):
        return args[0] > args[1]


class IsGte(Operator):
    """
    Сравнение >=.
    """
    sign = '>='
    description = 'Сравнение >= двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float, bool, datetime]),
        MandatoryArg('Значение2', 1, [int, float, bool, datetime]),
    ]

    def _operation(self, *args):
        return args[0] >= args[1]


class IsLt(Operator):
    """
    Сравнение <.
    """
    sign = '<'
    description = 'Сравнение < двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float]),
        MandatoryArg('Значение2', 1, [int, float]),
    ]

    def _operation(self, *args):
        return args[0] < args[1]


class IsLte(Operator):
    """
    Сравнение <=.
    """
    sign = '<='
    description = 'Сравнение <= двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [int, float]),
        MandatoryArg('Значение2', 1, [int, float]),
    ]

    def _operation(self, *args):
        return args[0] <= args[1]


class IsEq(Operator):
    """
    Сравнение ==.
    """
    sign = '=='
    description = 'Сравнение == двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [str, int, float, bool, datetime, list]),
        MandatoryArg('Значение2', 1, [str, int, float, bool, datetime, list]),
    ]

    def _operation(self, *args):
        return args[0] == args[1]


class IsNeq(Operator):
    """
    Сравнение !=.
    """
    sign = '!='
    description = 'Сравнение != двух значений'
    args_description = [
        MandatoryArg('Значение1', 0, [str, int, float, bool, datetime, list]),
        MandatoryArg('Значение2', 1, [str, int, float, bool, datetime, list]),
    ]

    def _operation(self, *args):
        return args[0] != args[1]


class Or(Operator):
    """
    Логическое ИЛИ
    """
    sign = '|'
    description = 'Логическое ИЛИ'
    args_description = [
        MandatoryArg('Значение1', 0),
        MandatoryArg('Значение2', 1),
    ]

    def _operation(self, *args):
        left, right = args
        return left | right


class And(Operator):
    """
    Логическое И
    """
    sign = '&'
    description = 'Логическое И'
    args_description = [
        MandatoryArg('Значение1', 0),
        MandatoryArg('Значение2', 1),
    ]

    def _operation(self, *args):
        left, right = args
        return left & right
