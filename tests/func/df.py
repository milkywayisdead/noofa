from pandas import DataFrame, Series

from noofa.core.func import df as DF
from noofa.core.func.errors import (
    NotEnoughArguments,
    ArgumentTypeError,
)
from noofa.tests.base import NoofaTest


class TestDfFunctions(NoofaTest):
    """
    Тестирование функций работы с датафреймами.
    """
    @classmethod
    def setUpClass(cls):
        cls.df1 = DataFrame([
            {'a': 1, 'b': 'Hello', 'c': 3.14},
            {'a': 2, 'b': 'hell', 'c': 3.14},
            {'a': 2, 'b': 'ello', 'c': 3.14},
            {'a': 3, 'b': 'ohell', 'c': 3.14},
            {'a': 3, 'b': 'hellno', 'c': 3.14},
            {'a': 3, 'b': 'holle', 'c': 3.14},
        ])
        cls.df2 = DataFrame([
            {'a': 3, 'b': 'Hello', 'c': 3.14},
            {'a': 2, 'b': 'hell', 'c': 3.14},
            {'a': 2, 'b': 'ello', 'c': 3.14},
            {'a': 3, 'b': 'ohell', 'c': 3.14},
            {'a': 4, 'b': 'hellno', 'c': 3.14},
            {'a': 4, 'b': 'holle', 'c': 3.14},
        ])

    def test_join(self):
        f = DF.Join(self.df1, self.df2, 'a', 'a', 'inner')
        df = f()
        self.assertEqual(df.shape[0], 10)

    def test_join_raises_nea(self):
        f = DF.Join(self.df1, self.df2, 'a', 'a')
        self.assertRaises(NotEnoughArguments, f)

    def test_join_raises_ate(self):
        f = DF.Join(0, self.df2, 'a', 'a', 'inner')
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Join(self.df1, 0, 'a', 'a', 'inner')
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Join(self.df1, self.df2, 0, 'a', 'inner')
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Join(self.df1, self.df2, 'a', 0, 'inner')
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Join(self.df1, self.df2, 'a', 'a', 0)
        self.assertRaises(ArgumentTypeError, f)

    def test_union(self):
        f = DF.Union(self.df1, self.df2)
        df = f()
        self.assertEqual(df.shape[0], 12)

    def test_union_raises_nea(self):
        f = DF.Union(self.df1)
        self.assertRaises(NotEnoughArguments, f)

    def test_union_raises_ate(self):
        f = DF.Union(0, self.df2)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Union(self.df1, 0)
        self.assertRaises(ArgumentTypeError, f)

    def test_df_filter(self):
        f = DF.DfFilter('a', '>', 1)
        fd = f()
        self.assertIsInstance(fd, DF.DfFilterDict)
        self.assertCountEqual(list(fd._q.keys()), ['is_q', 'col_name', 'op', 'value'])

    def test_df_filter_raises_nea(self):
        f = DF.DfFilter('a', '>')
        self.assertRaises(NotEnoughArguments, f)

    def test_df_filter_raises_ate(self):
        f = DF.DfFilter(0, '>', 1)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.DfFilter('a', 0, 1)
        self.assertRaises(ArgumentTypeError, f)

    def test_filter(self):
        f = DF.Filter(self.df1, DF.DfFilter('a', '>', 1)())
        df = f()
        self.assertEqual(df.shape[0], 5)

    def test_filter_raises_nea(self):
        f = DF.Filter(self.df1)
        self.assertRaises(NotEnoughArguments, f)

    def test_filter_raises_ate(self):
        f = DF.Filter(0, DF.DfFilter('a', '>', 1))
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Filter(self.df1, 0)
        self.assertRaises(ArgumentTypeError, f)

    def test_add_column(self):
        f = DF.AddColumn(self.df1, 'd', 0)
        df = f()
        self.assertIn('d', df)

    def test_add_column_raises_nea(self):
        f = DF.AddColumn(self.df1, 'd')
        self.assertRaises(NotEnoughArguments, f)

    def test_add_column_raises_ate(self):
        f = DF.AddColumn(0, 'd', 0)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.AddColumn(self.df1, 0, 0)
        self.assertRaises(ArgumentTypeError, f)

    def test_head(self):
        f = DF.Head(self.df1, 3)
        df = f()
        self.assertEqual(df.shape[0], 3)

    def test_head_raises_nea(self):
        f = DF.Head(self.df1)
        self.assertRaises(NotEnoughArguments, f)

    def test_head_raises_ate(self):
        f = DF.Head(0, 1)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Head(self.df1, '1')
        self.assertRaises(ArgumentTypeError, f)

    def test_tail(self):
        f = DF.Tail(self.df1, 3)
        df = f()
        self.assertEqual(df.shape[0], 3)

    def test_tail_raises_nea(self):
        f = DF.Tail(self.df1)
        self.assertRaises(NotEnoughArguments, f)

    def test_tail_raises_ate(self):
        f = DF.Tail(0, 1)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Tail(self.df1, '1')
        self.assertRaises(ArgumentTypeError, f)

    def test_count(self):
        f = DF.DfCount(self.df1)
        self.assertEqual(f(), 6)

    def test_count_raises_nea(self):
        f = DF.DfCount()
        self.assertRaises(NotEnoughArguments, f)

    def test_count_raises_ate(self):
        f = DF.DfCount(0)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.Tail(self.df1, '1')
        self.assertRaises(ArgumentTypeError, f)

    def test_get_column(self):
        f = DF.GetColumn(self.df1, 'a')
        self.assertIsInstance(f(), Series)

    def test_get_column_raises_nea(self):
        f = DF.GetColumn(self.df1)
        self.assertRaises(NotEnoughArguments, f)

    def test_get_column_raises_ate(self):
        f = DF.GetColumn(0, 1)
        self.assertRaises(ArgumentTypeError, f)

        f = DF.GetColumn(self.df1, 0)
        self.assertRaises(ArgumentTypeError, f)

