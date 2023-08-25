from pandas import DataFrame

from noofa.tests.base import NoofaTest
from noofa.core.dataframes import panda_builder as pb


class TestPandaBuilder(NoofaTest):
    """
    Тестирование функций работы с дф.
    """
    @classmethod
    def setUpClass(cls):
        cls.df2 = DataFrame([
            {'a': 4, 'c': 'Hello'},
            {'a': 2, 'c': 'hell'},
            {'a': 1, 'c': 'ello'},
            {'a': 3, 'c': 'ohell'},
            {'a': 2, 'c': 'hellno'},
            {'a': 2, 'c': 'holle'},
        ])
        cls.df_na = DataFrame([
            {'a': 4, 'c': None},
            {'a': 2, 'c': 2.5},
            {'a': 1, 'c': 3.14},
            {'a': 3, 'c': 2.7},
            {'a': 2, 'c': None},
            {'a': 2, 'c': None},
        ])
        cls.bad_filter = {
            'col_name': 'a',
            'op': 'non_ex',
            'value': 1,
            'is_q': False,
        }
        cls.filter = {
            'col_name': 'a',
            'op': '>',
            'value': 1,
            'is_q': False,
        }

    def setUp(self):
        self.df1 = DataFrame([
            {'a': 1, 'b': 'Hello'},
            {'a': 2, 'b': 'hell'},
            {'a': 2, 'b': 'ello'},
            {'a': 3, 'b': 'ohell'},
            {'a': 3, 'b': 'hellno'},
            {'a': 3, 'b': 'holle'},
        ])

    def test_new_and_empty(self):
        self.assertIsInstance(pb.new(), DataFrame)
        self.assertIsInstance(pb.empty(), DataFrame)

    def test_join(self):
        df = pb.join(self.df1, self.df2, ['a', 'a'], 'inner')
        r, c = df.shape
        self.assertEqual([r, c], [10, 3])

    def test_union_bad(self):
        self.assertRaises(Exception, pb.union, [])

        df = pb.union([self.df1])
        r, c = df.shape
        r1, c1 = self.df1.shape
        self.assertEqual([r, c], [r1, c1])

    def test_union(self):
        df = pb.union([self.df1, self.df2])
        r1 = self.df1.shape[0]
        r2 = self.df2.shape[0]
        r = df.shape[0]
        self.assertEqual([r1 + r2, 3], [r, 3])

    def test_add_column(self):
        col = 'd'
        cols = self.df1.shape[1]
        df = pb.add_column(self.df1, col, 1)
        cols1 = df.shape[1]
        self.assertTrue(cols1 == cols + 1 and col in df)

        df = pb.add_column(self.df1, col, 1)
        cols2 = df.shape[1]
        self.assertTrue(cols1 == cols2 and col in df)

    def test_add_columns(self):
        to_add = {'d': 1, 'e': 2}
        cols = self.df1.shape[1]
        df = pb.add_columns(self.df1, to_add)
        cols1 = df.shape[1]
        self.assertEqual(cols1, cols + 2)

        for col in to_add.keys():
            self.assertIn(col, df)

    def test_rename(self):
        cols_to_rename = {'a': 'A', 'b': 'B'}
        df = pb.rename_columns(self.df1, cols_to_rename)
        for prev, new in cols_to_rename.items():
            self.assertNotIn(prev, df)
            self.assertIn(new, df)

    def test_drop_empty(self):
        cols = self.df1.shape[1]
        df = pb.drop_columns(self.df1, [])
        self.assertEqual(cols, df.shape[1])

    def test_drop_multiple(self):
        cols = self.df1.shape[1]
        to_drop = ['a', 'b']
        df = pb.drop_columns(self.df1, to_drop)
        self.assertEqual(cols - 2, df.shape[1])
        for col in to_drop:
            self.assertNotIn(col, df)

    def test_filter_bad(self):
        self.assertRaises(KeyError, pb.filter, self.df1, [self.bad_filter])

    def test_filter(self):
        df = pb.filter(self.df1, [self.filter])
        self.assertEqual(df.shape[0], 5)

    def test_astype_simple(self):
        col = 'a'
        df = pb.astype(self.df1, col, 'str')
        self.assertEqual(str(df[col].dtype), 'object')

    def test_astype_int_to_dt(self):
        col = 'a'
        df = pb.astype(self.df1, col, 'datetime')
        self.assertTrue(str(df[col].dtype).startswith('datetime64'))

    def test_astype_dt_to_int(self):
        col = 'a'
        df = pb.astype(self.df1, col, 'datetime')
        df = pb.astype(df, col, 'int')
        self.assertEqual(str(df[col].dtype), 'int64')

    def test_astype_dt_to_float(self):
        col = 'a'
        df = pb.astype(self.df1, col, 'datetime')
        df = pb.astype(df, col, 'float')
        self.assertEqual(str(df[col].dtype), 'float64')

    def test_fill_na(self):
        col = 'c'
        self.assertRaises(AssertionError,
            pb.fill_na, self.df_na, col, None)

        df = pb.fill_na(self.df_na, col, 1)
        self.assertFalse(df[col].isnull().values.any())

    def test_drop_na(self):
        df = pb.drop_na(self.df_na, 'c')
        self.assertEqual(df.shape[0], 3)

    def test_pivot_table_empty(self):
        self.assertIsInstance(
            pb.pivot_table(DataFrame(), aggfunc={}),
            DataFrame
        )
        self.assertIsInstance(
            pb.pivot_table(self.df1, aggfunc={}),
            DataFrame
        )

    def test_pivot_table(self):
        self.assertIsInstance(
            pb.pivot_table(self.df1, index='b', aggfunc={'a': ['sum']}),
            DataFrame
        )
