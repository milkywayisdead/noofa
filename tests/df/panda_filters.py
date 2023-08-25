from pandas import DataFrame
from noofa.tests.base import NoofaTest
from noofa.core.dataframes import filters


class TestPandaFilters(NoofaTest):
    """
    Тестирование фильтров датафреймов.
    """
    @classmethod
    def setUpClass(cls):
        cls.df = DataFrame([
            {'a': 1, 'b': 'Hello', 'c': 3.14},
            {'a': 2, 'b': 'hell', 'c': 3.14},
            {'a': 2, 'b': 'ello', 'c': 3.14},
            {'a': 3, 'b': 'ohell', 'c': 3.14},
            {'a': 3, 'b': 'hellno', 'c': 3.14},
            {'a': 3, 'b': 'holle', 'c': 3.14},
        ])

        cls.filter1 =     {
            'col_name': 'a',
            'op': '>',
            'value': 1,
            'is_q': False,
        }
        cls.filter2 =     {
            'col_name': 'a',
            'op': '<',
            'value': 3,
            'is_q': False,
        }

    def test_eq(self):
        pf = filters.PandaEq('a', 1)
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 1)

    def test_neq(self):
        pf = filters.PandaNeq('a', 1)
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 5)

    def test_gt(self):
        pf = filters.PandaGt('a', 1)
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 5)

    def test_gte(self):
        pf = filters.PandaGte('a', 1)
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 6)

    def test_lt(self):
        pf = filters.PandaLt('a', 3)
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 3)

    def test_lte(self):
        pf = filters.PandaLte('a', 3)
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 6)

    def test_contains(self):
        pf = filters.PandaContains('b', 'el')
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 5)

    def test_startswith(self):
        pf = filters.PandaStartsWith('b', 'he')
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 3)

    def test_endswith(self):
        pf = filters.PandaEndsWith('b', 'lo')
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 2)

    def test_in(self):
        pf = filters.PandaIn('b', ['holle', 'hell'])
        pf.df = self.df
        filtered = self.df[pf.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 2)

    def test_empty_panda_q(self):
        pq = filters.PandaQ()
        self.assertTrue(pq.is_empty)

    def test_simple_panda_q(self):
        pf = filters.PandaIn('b', ['holle', 'hell'])
        pf.df = self.df
        pq = filters.PandaQ(pf)
        filtered = self.df[pq.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 2)

    def test_panda_q_and(self):
        pf1 = filters.PandaGt('a', 1)
        pf1.df = self.df
        pf2 = filters.PandaLt('a', 3)
        pf2.df = self.df

        pq = filters.PandaQ(pf1) & filters.PandaQ(pf2)
        filtered = self.df[pq.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 2)

    def test_panda_q_or(self):
        pf1 = filters.PandaEq('a', 1)
        pf1.df = self.df
        pf2 = filters.PandaEq('a', 3)
        pf2.df = self.df

        pq = filters.PandaQ(pf1) | filters.PandaQ(pf2)
        filtered = self.df[pq.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 4)

    def test_parse_filter(self):
        f = filters._parse_filter(self.df, self.filter1)
        self.assertIsInstance(f, filters.PandaQ)
        filtered = self.df[f.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 5)

    def test_parse_complex_filter(self):
        cmplx = {
            'is_q': True,
            'op': 'and',
            'filters': [
                self.filter1,
                self.filter2
            ]
        }
        f = filters._parse_filter(self.df, cmplx)
        self.assertIsInstance(f, filters.PandaQ)
        filtered = self.df[f.filter]
        n = filtered.shape[0]
        self.assertEqual(n, 2)

