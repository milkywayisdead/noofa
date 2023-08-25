from pandas import DataFrame, Series

from noofa.tests.base import NoofaTest
from noofa.core.func import datastruct as DS
from noofa.core.func.errors import (
    NotEnoughArguments,
    ArgumentTypeError,
)


class TestDatastructFunctions(NoofaTest):
    """
    Тестирование функций работы со списками.
    """
    @classmethod
    def setUpClass(cls):
        cls.list = (1, 2, 3)
        cls.series = Series(cls.list)
        cls.df = DataFrame({'a': cls.list})

    def test_empty_list(self):
        f = DS.List()
        self.assertEqual(f(), [])

    def test_list(self):
        f = DS.List(1, 2, 3)
        self.assertEqual(f(), [1, 2, 3])

    def test_series_to_list(self):
        f = DS.ToList(self.series)
        self.assertEqual(f(), [1, 2, 3])

    def test_df_to_list(self):
        f = DS.ToList(self.df)
        self.assertEqual(f(), [1, 2, 3])

    def test_to_list_raises_nea(self):
        f = DS.ToList()
        self.assertRaises(NotEnoughArguments, f)

    def test_to_list_raises_ate(self):
        for arg in ['1', 1, 2.1, False]:
            f = DS.ToList(arg)
            with self.subTest(arg):
                self.assertRaises(ArgumentTypeError, f)
