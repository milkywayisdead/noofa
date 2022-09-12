from .base import StatisticsFunc, MandatoryArg, NonMandatoryArg
from ..dataframes.panda_builder import pd


class Mean(StatisticsFunc):
    """
    Функция нахождения среднего значения.
    """
    description = 'Функция нахождения среднего значения'
    args_description = [
        MandatoryArg('Последовательность значений', 0),
    ]

    def _operation(self, *args):
        seq = args[0]
        if isinstance(seq, list):
            seq = pd.Series(seq)
        return float(seq.mean())


class Median(StatisticsFunc):
    """
    Функция нахождения медианы.
    """
    description = 'Функция нахождения медианы'
    args_description = [
        MandatoryArg('Последовательность значений', 0),
    ]

    def _operation(self, *args):
        seq = args[0]
        if isinstance(seq, list):
            seq = pd.Series(seq)
        return float(seq.median())


class Mode(StatisticsFunc):
    """
    Функция нахождения моды.
    """
    description = 'Функция нахождения моды'
    args_description = [
        MandatoryArg('Последовательность значений', 0),
    ]

    def _operation(self, *args):
        seq = args[0]
        if isinstance(seq, list):
            seq = pd.Series(seq)
        return float(seq.mode().loc(0)[0])


class Min(StatisticsFunc):
    """
    Минимальное число в наборе.
    """
    description = 'Выбор наименьшего числа в наборе'
    args_description = [
        MandatoryArg('Набор чисел', 0),
    ]

    def _operation(self, *args):
        seq = args[0]
        if isinstance(seq, list):
            seq = pd.Series(seq)
        return float(seq.min())


class Max(StatisticsFunc):
    """
    Максимальное число в наборе.
    """
    description = 'Выбор наибольшего числа в наборе'
    args_description = [
        MandatoryArg('Набор чисел', 0),
    ]

    def _operation(self, *args):
        seq = args[0]
        if isinstance(seq, list):
            seq = pd.Series(seq)
        return float(seq.max())


class Stdev(StatisticsFunc):
    """
    Стандартное отклонение.
    """
    description = 'Функция вычисления стандартного отклонения'
    args_description = [
        MandatoryArg('Последовательность значений', 0),
        NonMandatoryArg('Отклонение для выборки/совокупности', 1),
    ]

    def _operation(self, *args):
        seq = args[0]
        try:
            ddof = args[1]
        except IndexError:
            ddof = 1
        if isinstance(seq, list):
            seq = pd.Series(seq)
        return float(seq.std(ddof=ddof))