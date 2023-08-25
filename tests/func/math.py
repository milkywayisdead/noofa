import math
from pandas import DataFrame
from datetime import datetime

from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import numbers as N


class TestMathFunctions(NoofaFunctionTest):
    """
    Тестирование функций в выражениях.
    """
    @classmethod
    def setUpClass(cls):
        cls.add_cases_from_list(_CASES)


_df = DataFrame()
_dt = datetime.now()
_bad_args = ('1', _dt, _df)


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
    (N.Abs, ((-1, 1), (1, 1)), _bad_args),
    (N.Acos, ((1, math.acos(1)), ), _bad_args),
    (N.Asin, ((1, math.asin(1)), ), _bad_args),
    (N.Atan, ((1, math.atan(1)), ), _bad_args),
    (N.Ceil, ((3.14, 4), ), _bad_args),
    (N.Cos, ((1, math.cos(1)), ), _bad_args),
    (N.Cot, ((1, 1/math.tan(1)), ), _bad_args),
    (N.Degrees, ((1, math.degrees(1)), ), _bad_args),
    (N.Div, (((10, 4), 2.5), ), (('1', 1), (_dt, 1), (1, _df)), (1, )),
    (N.Idiv, (((10, 4), 2), ), (('1', 1), (_dt, 1), (1, _df)), (1, )),
    (N.Exp, ((2, math.exp(2)), ), _bad_args),
    (N.Floor, ((3.14, 3), ), _bad_args),
    (N.Ln, ((3, math.log(3)), ), _bad_args),
    (N.Pow, (((3, 3), 27), ), (('1', 1), (_dt, 1), (1, _df)), (1, )),
    (N.Radians, ((1, math.radians(1)), ), _bad_args),
    (N.Round, ((3.14, 3), ((3.1415926, 2), 3.14)), (('1', 1), (_dt, 1), (1, _df))),
    (N.Sin, ((1, math.sin(1)), ), _bad_args),
    (N.Sqrt, ((9, 3), ), _bad_args),
    (N.Sum, ((1, 1), ([1, 2, 3], 6)), (), ()),
    (N.Tan, ((1, math.tan(1)), ), _bad_args),
]
