from pandas import DataFrame, Series
from datetime import datetime

from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import strings as S


class TestStringsFunctions(NoofaFunctionTest):
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
    (S.Contains,
        (
            (('12', '1'), True),
            (('12', '3'), False),
        ),
        (('1', 1), ('2', 3.14), ),
        (1, ),
    ),
    (S.Endswith,
        (
            (('12', '2'), True),
            (('12', '3'), False),
        ),
        (('1', 1), ('2', 3.14), ),
        (1, ),
    ),
    (S.Startswith,
        (
            (('12', '1'), True),
            (('12', '3'), False),
        ),
        (('1', 1), ('2', 3.14), ),
        (1, ),
    ),
    (S.Len,
        (
            ('0123', 4),
        ),
        _bad_args,
        (),
    ),
    (S.Lower,
        (
            ('TRUE', 'true'),
        ),
        _bad_args,
        (),
    ),
    (S.Upper,
        (
            ('true', 'TRUE'),
        ),
        _bad_args,
        (),
    ),
    (S.Concat,
        (
            (('Hello', ', World'), 'Hello, World'),
            (('Hello', ',', ' ', 'World'), 'Hello, World'),
        ),
        ((1, ''), (3.14, ''), (_dt, '')),
        ('', ),
    ),
    (S.Join,
        (
            ((',', '1', '2'), '1,2'),
            ((', ', '1', '2', '3'), '1, 2, 3'),
        ),
        (('1', 1, ''), ('2', 3.14, ''), ),
        (1, ),
    ),
]
