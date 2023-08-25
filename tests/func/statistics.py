from pandas import DataFrame, Series
from datetime import datetime, time, date

from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import statistics as S


class TestStatisticsFunctions(NoofaFunctionTest):
    """
    Тестирование статистических функций.
    """
    @classmethod
    def setUpClass(cls):
        cls.add_cases_from_list(_CASES)


_dt = datetime.now()
_bad_args = (_dt, _dt.date(), _dt.time(), 1, 3.14, '', False)


"""
Содержимое кортежей в списке _CASES:
(
    Функция,
    сабкейсы (кортеж из аргументов и ожидаемого результата),
    аргументы для проверки ошибки по типу аргумента,
    аргументы для проверки ошибки по кол-ву аргументов
)
"""
_CASES = [
    (S.Mean, (), _bad_args, ()),
    (S.Median, (), _bad_args, ()),
    (S.Mode, (), _bad_args, ()),
    (S.Min, (), _bad_args, ()),
    (S.Max, (), _bad_args, ()),
    (S.Stdev, (), _bad_args, ()),
    (S.Variance, (), _bad_args, ()),
]
