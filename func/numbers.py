"""
Математические функции.
"""

import math
from .base import MathFunc


class Abs(MathFunc):
    """
    Модуль числа.
    """
    description = 'Получение модуля числа'
    operation = abs
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Acos(MathFunc):
    """
    Арккосинус числа.
    """
    description = 'Получение арккосинуса числа'
    operation = math.acos
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Asin(MathFunc):
    """
    Арксинус числа.
    """
    description = 'Получение арксинуса числа'
    operation = math.asin
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Atan(MathFunc):
    """
    Арктангенс числа.
    """
    description = 'Получение арктангенса числа'
    operation = math.atan
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Atan2(MathFunc):
    """
    Арктангенс частного двух чисел.
    """
    description = 'Получение арктангенса x/y'
    operation = math.atan2
    args_description = [
        {'name': 'x', 'index': 0, 'is_mandatory': True},
        {'name': 'y', 'index': 1, 'is_mandatory': True},
    ]


class Ceil(MathFunc):
    """
    Округление числа до ближайшего целого
    в большую сторону.
    """
    description = 'Округление числа в большую сторону'
    operation = math.ceil
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Cos(MathFunc):
    """
    Косинус угла в радианах.
    """
    description = 'Получение косинуса угла. Значение угла - в радианах'
    operation = math.cos
    args_description = [
        {'name': 'Угол(рад)', 'index': 0, 'is_mandatory': True},
    ]


class Cot(MathFunc):
    """
    Котангенс угла.
    """
    description = 'Получение котангенса угла. Значение угла - в радианах'
    args_description = [
        {'name': 'Угол(рад)', 'index': 0, 'is_mandatory': True},
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
        {'name': 'Радианы', 'index': 0, 'is_mandatory': True},
    ]


class Div(MathFunc):
    """
    Деление.
    """
    description = 'Деление двух чисел x/y с остатком'
    args_description = [
        {'name': 'x', 'index': 0, 'is_mandatory': True},
        {'name': 'y', 'index': 1, 'is_mandatory': True},
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
        {'name': 'x', 'index': 0, 'is_mandatory': True},
        {'name': 'y', 'index': 1, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        try:
            return arg[0]//arg[1]
        except ZeroDivisionError:
            return math.inf


class Exp(MathFunc):
    """
    Вычисление экспоненты.
    """
    description = 'Вычисление экспоненты'
    operation = math.exp
    args_description = [
        {'name': 'Степень', 'index': 0, 'is_mandatory': True},
    ]


class Floor(MathFunc):
    """
    Округление до ближайшего целого 
    в меньшую сторону.
    """
    description = 'Округление числа в меньшую сторону'
    operation = math.floor
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Ln(MathFunc):
    """
    Натуральный логарифм числа.
    """
    description = 'Натуральный логарифм числа'
    operation = math.log
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
    ]


class Log(MathFunc):
    """
    Вычисление логарифма x по основанию y.
    """
    operation = math.log
    description = 'Вычисление логарифма числа по основанию'
    operation = math.log
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
        {'name': 'Основание', 'index': 1, 'is_mandatory': True},
    ]


class Min(MathFunc):
    """
    Минимальное число в наборе.
    """
    description = 'Выбор наименьшего числа в наборе'
    operation = min
    args_description = [
        {'name': 'Набор чисел', 'index': 0, 'is_mandatory': True},
    ]


class Max(MathFunc):
    """
    Максимальное число в наборе.
    """
    description = 'Выбор наибольшего числа в наборе'
    operation = max
    args_description = [
        {'name': 'Набор чисел', 'index': 0, 'is_mandatory': True},
    ]


class Pow(MathFunc):
    """
    Возведение x в степень y.
    """
    description = 'Возведение x в степень y'
    operation = pow
    args_description = [
        {'name': 'x', 'index': 0, 'is_mandatory': True},
        {'name': 'y', 'index': 1, 'is_mandatory': True},
    ]


class Radians(MathFunc):
    """
    Перевод градусов в радианы.
    """
    description = 'Перевод градусов в радианы'
    operation = math.radians
    args_description = [
        {'name': 'Градусы', 'index': 0, 'is_mandatory': True},
    ]


class Round(MathFunc):
    """
    Округление числа до определённого кол-ва знаков после запятой.
    """
    description = 'Округление числа до определённого количества n знаков после запятой'
    operation = round
    args_description = [
        {'name': 'Число', 'index': 0, 'is_mandatory': True},
        {'name': 'n', 'index': 1, 'is_mandatory': False},
    ]


class Sin(MathFunc):
    """
    Синус угла в радианах.
    """
    description = 'Получение синуса угла. Значение угла - в радианах'
    operation = math.sin
    args_description = [
        {'name': 'Угол(рад)', 'index': 0, 'is_mandatory': True},
    ]


class Sqrt(MathFunc):
    """
    Извлечение квадратного корня числа.
    """
    description = 'Перевод радиан в градусы'
    operation = math.degrees
    args_description = [
        {'name': 'Радианы', 'index': 0, 'is_mandatory': True},
    ]


class Sum(MathFunc):
    description = 'Сумма нескольких чисел'
    args_description = [
        {'name': 'Слагаемое1', 'index': 0, 'is_mandatory': True},
        {'name': 'Слагаемое2', 'index': 1, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        result = 0
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
        {'name': 'Угол(рад)', 'index': 0, 'is_mandatory': True},
    ]