from pandas import DataFrame
from datetime import datetime, date, time

from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import date as DT


class TestDateFunctions(NoofaFunctionTest):
    """
    Тестирование функций работы с датой-временем.
    """
    @classmethod
    def setUpClass(cls):
        cls.add_cases_from_list(_CASES)

    def test_date(self):
        f = DT.Date()
        d1 = f()
        self.assertIsInstance(d1, date)
        d2 = datetime.now().date()
        self.assertEqual(d1, d2)

    def test_time(self):
        f = DT.Time()
        self.assertIsInstance(f(), time)

    def test_now(self):
        f = DT.Now()
        self.assertIsInstance(f(), datetime)


_df = DataFrame()

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
    (DT.SecToDate, ((12345, datetime(1970, 1, 1, 3, 25, 45)), ), ('1', [], _df)),
    (DT.MsecToDate, ((12345000, datetime(1970, 1, 1, 3, 25, 45)), ), ('1', [], _df)),
    (
        DT.SecToDateStr,
        ((12345, '1970-01-01 03:25:45'), ((12345, '%H:%M:%S %d-%m-%Y'), '03:25:45 01-01-1970')),
        ('1', [], _df, (12345, 1)),
        (),
    ),
    (
        DT.MsecToDateStr,
        ((12345000, '1970-01-01 03:25:45'), ((12345000, '%H:%M:%S %d-%m-%Y'), '03:25:45 01-01-1970')),
        ('1', [], _df, (12345, 1)),
        (),
    ),
    (DT.DateToSec, ((datetime(1970, 1, 1, 3, 25, 45), 12345), ), ('1', [], _df)),
    (
        DT.DateToStr,
        (
            (datetime(1970, 1, 1, 3, 25, 45), '1970-01-01 03:25:45'),
            ((datetime(1970, 1, 1, 3, 25, 45), '%H:%M:%S %d-%m-%Y'), '03:25:45 01-01-1970'),
            (date(1970, 1, 1), '1970-01-01'),
            ((date(1970, 1, 1), '%d-%m-%Y'), '01-01-1970'),
            (time(3, 25, 45), '03:25:45'),
            ((time(3, 25, 45), '%H-%M-%S'), '03-25-45'),
        ),
        ('1', [], _df, (12345, 1), False),
        (),
    ),
    (
        DT.StrToDate,
        (
            ('1970-01-01 03:25:45', datetime(1970, 1, 1, 3, 25, 45)),
            (('03:25:45 01-01-1970', '%H:%M:%S %d-%m-%Y'), datetime(1970, 1, 1, 3, 25, 45)),
        ),
        ([], _df, (12345, 1), False),
        (),
    ),
]
