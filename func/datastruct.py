"""
Структуры данных.
"""

from .base import DatastructFunc, NonMandatoryArg, MandatoryArg


class List(DatastructFunc):
    """
    Функция создания списка элементов.
    """
    description = 'Функция создания списка элементов'
    args_description = [
        NonMandatoryArg('Элемент1', 0),
        NonMandatoryArg('Элемент2', 1),
        NonMandatoryArg('Элемент n', 2),
    ]

    def _operation(self, *args):
        return [arg for arg in args] 