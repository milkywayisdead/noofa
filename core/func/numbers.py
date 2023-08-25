"""
Математические функции.
"""

import math
from .base import MathFunc, NonMandatoryArg, MandatoryArg


class Abs(MathFunc):
    """
    Модуль числа.
    """
    description = 'Получение модуля числа'
    operation = abs
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


class Acos(MathFunc):
    """
    Арккосинус числа.
    """
    description = 'Получение арккосинуса числа'
    operation = math.acos
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


class Asin(MathFunc):
    """
    Арксинус числа.
    """
    description = 'Получение арксинуса числа'
    operation = math.asin
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


class Atan(MathFunc):
    """
    Арктангенс числа.
    """
    description = 'Получение арктангенса числа'
    operation = math.atan
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


""" class Atan2(MathFunc):
    '''
    Арктангенс частного двух чисел.
    '''
    description = 'Получение арктангенса x/y'
    operation = math.atan2
    args_description = [
        MandatoryArg('x', 0),
        MandatoryArg('y', 1),
    ] """


class Ceil(MathFunc):
    """
    Округление числа до ближайшего целого
    в большую сторону.
    """
    description = 'Округление числа в большую сторону'
    operation = math.ceil
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


class Cos(MathFunc):
    """
    Косинус угла в радианах.
    """
    description = 'Получение косинуса угла. Значение угла - в радианах'
    operation = math.cos
    args_description = [
        MandatoryArg('Угол(рад)', 0, [int, float]),
    ]


class Cot(MathFunc):
    """
    Котангенс угла.
    """
    description = 'Получение котангенса угла. Значение угла - в радианах'
    args_description = [
        MandatoryArg('Угол(рад)', 0, [int, float]),
    ]

    def _operation(self, *args):
        try:
            return 1/math.tan(args[0])
        except ZeroDivisionError:
            return math.inf


class Degrees(MathFunc):
    """
    Перевод радиан в градусы.
    """
    description = 'Перевод радиан в градусы'
    operation = math.degrees
    args_description = [
        MandatoryArg('Радианы', 0, [int, float]),
    ]


class Div(MathFunc):
    """
    Деление.
    """
    description = 'Деление двух чисел x/y с остатком'
    args_description = [
        MandatoryArg('x', 0, [int, float]),
        MandatoryArg('y', 1, [int, float]),
    ]

    def _operation(self, *args):
        try:
            return args[0]/args[1]
        except ZeroDivisionError:
            return math.inf


class Idiv(MathFunc):
    """
    Целочисленное деление.
    """
    description = 'Целочисленное деление двух чисел x/y'
    args_description = [
        MandatoryArg('x', 0, [int, float]),
        MandatoryArg('y', 1, [int, float]),
    ]

    def _operation(self, *args):
        try:
            return args[0]//args[1]
        except ZeroDivisionError:
            return math.inf


class Exp(MathFunc):
    """
    Вычисление экспоненты.
    """
    description = 'Вычисление экспоненты'
    operation = math.exp
    args_description = [
        MandatoryArg('Степень', 0, [int, float]),
    ]


class Floor(MathFunc):
    """
    Округление до ближайшего целого 
    в меньшую сторону.
    """
    description = 'Округление числа в меньшую сторону'
    operation = math.floor
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


class Ln(MathFunc):
    """
    Натуральный логарифм числа.
    """
    description = 'Натуральный логарифм числа'
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]

    def _operation(self, *args):
        return math.log(args[0])


class Log(MathFunc):
    """
    Вычисление логарифма x по основанию y.
    """
    description = 'Вычисление логарифма числа по основанию'
    operation = math.log
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
        MandatoryArg('Основание', 1, [int, float]),
    ]

    def _operation(self, *args):
        return math.log(args[0], args[1])


class Pow(MathFunc):
    """
    Возведение x в степень y.
    """
    description = 'Возведение x в степень y'
    operation = pow
    args_description = [
        MandatoryArg('x', 0, [int, float]),
        MandatoryArg('y', 0, [int, float]),
    ]


class Radians(MathFunc):
    """
    Перевод градусов в радианы.
    """
    description = 'Перевод градусов в радианы'
    operation = math.radians
    args_description = [
        MandatoryArg('Градусы', 0, [int, float]),
    ]


class Round(MathFunc):
    """
    Округление числа до определённого кол-ва знаков после запятой.
    """
    description = 'Округление числа до определённого количества n знаков после запятой'
    operation = round
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
        NonMandatoryArg('n', 1, [int, float]),
    ]


class Sin(MathFunc):
    """
    Синус угла в радианах.
    """
    description = 'Получение синуса угла. Значение угла - в радианах'
    operation = math.sin
    args_description = [
        MandatoryArg('Угол(рад)', 0, [int, float]),
    ]


class Sqrt(MathFunc):
    """
    Извлечение квадратного корня числа.
    """
    description = 'Извлечение квадратного корня числа'
    operation = math.sqrt
    args_description = [
        MandatoryArg('Число', 0, [int, float]),
    ]


class Sum(MathFunc):
    description = 'Сумма нескольких чисел'
    args_description = [
        MandatoryArg('Слагаемое1', 0),
        NonMandatoryArg('Слагаемое2', 1),
    ]

    def _operation(self, *args):
        result = 0
        arg = args[0]
        if isinstance(arg, list):
            return sum(arg)
        else:
            try:
                return float(arg.sum()[0])
            except AttributeError:
                pass
        for arg in args:
            result += arg
        return result


class Tan(MathFunc):
    """
    Тангенс угла в радианах.
    """
    description = 'Получение тангенса угла. Значение угла - в радианах'
    operation = math.tan
    args_description = [
        MandatoryArg('Угол(рад)', 0, [int, float]),
    ]
