"""
Функции преобразования типов данных.
"""
from .base import TypeconvFunc, MandatoryArg


class To_Str(TypeconvFunc):
    """
    Преобразование в строку.
    """
    description = 'Преобразование в строку'
    args_description = [
        MandatoryArg('Значение', 0, [int, float, str]),
    ]

    def _operation(self, *args):
        return str(args[0])

    @property
    def name(self):
        return 'to_str'


class To_Float(TypeconvFunc):
    """
    Преобразование в тип float.
    """
    description = 'Преобразование в тип float'
    args_description = [
        MandatoryArg('Значение', 0, [str, int, float]),
    ]

    def _operation(self, *args):
        return float(args[0])

    @property
    def name(self):
        return 'to_float'


class To_Int(TypeconvFunc):
    """
    Преобразование в тип int.
    """
    description = 'Преобразование в тип int'
    args_description = [
        MandatoryArg('Значение', 0, [str, int, float]),
    ]

    def _operation(self, *args):
        return int(args[0])

    @property
    def name(self):
        return 'to_int'
