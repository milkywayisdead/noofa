from pandas import DataFrame, Series
from datetime import datetime

from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import typeconv as TC


class TestTypeConvFunctions(NoofaFunctionTest):
    """
    Тестирование функций преобразования типов.
    """
    @classmethod
    def setUpClass(cls):
        cls.add_cases_from_list(_CASES)


_dt = datetime.now()
_bad_args = [_dt, _dt.date(), _dt.time(), DataFrame(), Series((1,2))]

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
    (TC.To_Str, (('1', '1'), (1, '1'), (1.1, '1.1')), _bad_args, ()),
    (TC.To_Float, (('1', 1.0), (1, 1.0), (1.1, 1.1)), _bad_args, ()),
    (TC.To_Int, (('1', 1), (1, 1), (1.1, 1)), _bad_args, ()),
]
