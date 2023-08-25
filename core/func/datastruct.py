"""
Структуры данных.
"""

from .base import DatastructFunc, NonMandatoryArg, MandatoryArg
from ..dataframes.panda_builder import pd


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


class ToList(DatastructFunc):
    """
    Функция преобразования в список элементов.
    """
    description = 'Функция преобразования в список элементов'
    args_description = [
        MandatoryArg('Элемент', 0, [pd.DataFrame, pd.Series]),
    ]

    @classmethod
    def get_name(cls):
        return 'to_list'

    def _operation(self, *args):
        arg = args[0]
        if isinstance(arg, pd.DataFrame):
            cols = arg.columns
            if len(cols) == 1:
                return arg[cols[0]].to_list()
        elif isinstance(arg, pd.Series):
            return arg.to_list()
        return []
