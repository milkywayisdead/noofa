import math
from .base import Func


def _cot(x):
    try:
        return 1/math.tan(x)
    except ZeroDivisionError:
        return math.inf

def _div(x, y):
    try:
        return x/y
    except ZeroDivisionError:
        return math.inf

def _idiv(x, y):
    try:
        return x//y
    except ZeroDivisionError:
        return math.inf


class Abs(Func):
    """
    Модуль числа.
    """
    operation = abs
    operands_num = 1


class Acos(Func):
    """
    Арккосинус числа.
    """
    operation = math.acos
    operands_num = 1


class Asin(Func):
    """
    Арксинус числа.
    """
    operation = math.asin
    operands_num = 1


class Atan(Func):
    """
    Арктангенс числа.
    """
    operation = math.atan
    operands_num = 1


class Atan2(Func):
    """
    Арктангенс частного двух чисел.
    """
    operation = math.atan2
    operands_num = 2
    unpack_values = True


class Ceil(Func):
    """
    Округление числа до ближайшего целого
    в большую сторону.
    """
    operation = math.ceil
    operands_num = 1


class Cos(Func):
    """
    Косинус угла в радианах.
    """
    operation = math.cos
    operands_num = 1


class Cot(Func):
    """
    Котангенс угла.
    """
    operation = _cot
    operands_num = 1


class Degrees(Func):
    """
    Перевод радиан в градусы.
    """
    operation = math.degrees
    operands_num = 1


class Div(Func):
    """
    Деление.
    """
    operation = _div
    operands_num = 2
    unpack_values = True


class Idiv(Func):
    """
    Целочисленное деление.
    """
    operation = _idiv
    operands_num = 2
    unpack_values = True


class Exp(Func):
    """
    Вычисление экспоненты.
    """
    operation = math.exp
    operands_num = 1


class Floor(Func):
    """
    Округление до ближайшего целого 
    в меньшую сторону.
    """
    operation = math.floor
    operands_num = 1


class Ln(Func):
    """
    Натуральный логарифм числа.
    """
    operation = math.log
    operands_num = 1


class Log(Func):
    """
    Вычисление логарифма x по основанию y.
    """
    operation = math.log
    operands_num = 2
    unpack_values = True


class Min(Func):
    """
    Минимальное число в наборе.
    """
    operation = min
    operands_num = -1


class Max(Func):
    """
    Максимальное число в наборе.
    """
    operation = max
    operands_num = -1


class Pow(Func):
    """
    Возведение x в степень y.
    """
    operation = pow
    operands_num = 2
    unpack_values = True


class Radians(Func):
    """
    Перевод градусов в радианы.
    """
    operation = math.radians
    operands_num = 1


class Round(Func):
    """
    Округление числа до определённого кол-ва знаков после запятой.
    """
    operation = round
    operands_num = 2
    unpack_values = True


class Sin(Func):
    """
    Синус угла в радианах.
    """
    operation = math.sin
    operands_num = 1


class Sqrt(Func):
    """
    Извлечение квадратного корня числа.
    """
    operation = math.sqrt
    operands_num = 1


class Sum(Func):
    """
    Сумма чисел.
    """
    operation = sum
    operands_num = -1


class Tan(Func):
    """
    Тангенс угла в радианах.
    """
    operation = math.tan
    operands_num = 1