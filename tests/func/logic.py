from pandas import DataFrame, Series
from datetime import datetime

from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import logic as L


class TestLogicFunctions(NoofaFunctionTest):
    """
    Тестирование функций преобразования типов.
    """
    @classmethod
    def setUpClass(cls):
        cls.add_cases_from_list(_CASES)


_bad_args = (DataFrame(), Series((1,2)))

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
    (L.BoolTrue, (((), bool, 'isinstance'), ((), True)), (), None),
    (L.BoolFalse, (((), bool, 'isinstance'), ((), False)), (), None),
    (
        L.Eq,
        (
            (('1', '1'), True), (('1', '2'), False),
            ((1, 1), True), ((1, 2), False),
            ((1.1, 1.1), True), ((1.2, 2.1), False),
            ((True, True), True), ((True, False), False),
            ((datetime(1970, 1, 1), datetime(1970, 1, 1)), True),
            ((datetime(1970, 1, 2), datetime(1970, 1, 1)), False),
            (([1, 1], [1, 1]), True), (([1, 2], [2, 1]), False),
        ),
        (_bad_args, ),
        (False, ),
    ),
    (
        L.Neq,
        (
            (('1', '1'), False), (('1', '2'), True),
            ((1, 1), False), ((1, 2), True),
            ((1.1, 1.1), False), ((1.2, 2.1), True),
            ((True, True), False), ((True, False), True),
            ((datetime(1970, 1, 1), datetime(1970, 1, 1)), False),
            ((datetime(1970, 1, 2), datetime(1970, 1, 1)), True),
            (([1, 1], [1, 1]), False), (([1, 2], [2, 1]), True),
        ),
        (_bad_args, ),
        (False, ),
    ),
    (
        L.Gt,
        (
            ((1, 1), False), ((2, 1), True),
            ((1.1, 1.1), False), ((2.2, 2.1), True),
            ((True, False), True), ((False, True), False),
            ((datetime(1970, 1, 2), datetime(1970, 1, 1)), True),
            ((datetime(1970, 1, 1), datetime(1970, 1, 2)), False),
        ),
        (_bad_args, ('1', '2'), ),
        (False, ),
    ),
    (
        L.Gte,
        (
            ((1, 1), True), ((2, 1), True), ((1, 2), False),
            ((1.1, 1.1), True), ((2.2, 2.1), True), ((2.2, 2.3), False),
            ((True, True), True), ((False, True), False), ((True, False), True),
            ((datetime(1970, 1, 2), datetime(1970, 1, 1)), True),
            ((datetime(1970, 1, 1), datetime(1970, 1, 1)), True),
            ((datetime(1970, 1, 1), datetime(1970, 1, 2)), False),
        ),
        (_bad_args, ('1', '2'), ),
        (False, ),
    ),
    (
        L.Lt,
        (
            ((1, 1), False), ((2, 3), True),
            ((1.1, 1.1), False), ((2.2, 2.3), True),
            ((True, False), False), ((False, True), True),
            ((datetime(1970, 1, 2), datetime(1970, 1, 1)), False),
            ((datetime(1970, 1, 1), datetime(1970, 1, 2)), True),
        ),
        (_bad_args, ('1', '2'), ),
        (False, ),
    ),
    (
        L.Lte,
        (
            ((1, 1), True), ((2, 1), False), ((1, 2), True),
            ((1.1, 1.1), True), ((2.2, 2.1), False), ((2.2, 2.3), True),
            ((True, True), True), ((False, True), True), ((True, False), False),
            ((datetime(1970, 1, 2), datetime(1970, 1, 1)), False),
            ((datetime(1970, 1, 1), datetime(1970, 1, 1)), True),
            ((datetime(1970, 1, 1), datetime(1970, 1, 2)), True),
        ),
        (_bad_args, ('1', '2'), ),
        (False, ),
    ),
    (L.If, (((True, 1, 2), 1), ((False, 1, 2), 2)), (), (False, )),
    (L.And, (((True, False), False), ((True, True), True)), (), (False, )),
    (L.Or, (((True, False), True), ((True, True), True), ((False, False), False)), (), (False, )),
    (L.In, (
        ((1, [1, 2]), True),
        (('1', '12'), True),
        ((10, [1, 2]), False),
        (('10', '12'), False),
        ), (), (False, )
    ),
    (L.Switch,
        (
            ((True, 0, (False, 2), (True, 1)), 1),
        ),
        (),
        (False, )
    )
]
