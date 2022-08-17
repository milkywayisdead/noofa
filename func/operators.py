"""
Операторы.
"""
from .base import Operator, NonMandatoryArg, MandatoryArg


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
        return args[0] + args[1]


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
        return args[0] - args[1]


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