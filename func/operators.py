"""
Операторы.
"""
from .base import Operator, MandatoryArg


class Add(Operator):
    """
    Сумма двух чисел.
    """
    sign = '+'
    description = 'Сумма двух чисел'
    args_description = [
        MandatoryArg('Число1', 0),
        MandatoryArg('Число2', 1),
    ]

    def _operation(self, *args):
        left, right = args
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
        MandatoryArg('Число1', 0),
        MandatoryArg('Число2', 1),
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
        MandatoryArg('Число1', 0),
        MandatoryArg('Число2', 1),
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
        MandatoryArg('Число1', 0),
        MandatoryArg('Число2', 1),
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
        MandatoryArg('Значение1', 0),
        MandatoryArg('Значение2', 1),
    ]

    def _operation(self, *args):
        return args[0] > args[1]


class IsGt(Operator):
    """
    Сравнение <.
    """
    sign = '<'
    description = 'Сравнение < двух значений'
    args_description = [
        MandatoryArg('Значение1', 0),
        MandatoryArg('Значение2', 1),
    ]

    def _operation(self, *args):
        return args[0] < args[1]