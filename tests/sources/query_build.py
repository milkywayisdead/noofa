from noofa.tests.base import NoofaTest
from noofa.core.sources import utils
from noofa.core.sources.query import (
    Q,
    Table,
    NoSuchFieldError,
    TableHasNoFields,
    SelectQuery,
    GtFilter,
    LtFilter,
    EqFilter,
    NeqFilter,
    GeFilter,
    LeFilter,
    EqFilter,
    ContainsFilter,
    StartsWithFilter,
    EndsWithFilter,
    InFilter,
    NotInFilter,
)


class TestQueryComponents(NoofaTest):
    """
    Тестирование компонентов запроса.
    """
    @classmethod
    def setUpClass(cls):
        cls.table = Table(
            'table1',
            ['col1', 'col2', 'col3'],
            enquote=True
        )
        cls.table2 = Table(
            'table2',
            ['col1', 'col2', 'col3'],
            enquote=True
        )
        cls.table_no_enquote = Table(
            'table1',
            ['col1', 'col2', 'col3'],
            enquote=False
        )

    def setUp(self):
        self.maxDiff = None
        self.query = self.table.select()

    def test_table_has_field(self):
        self.assertTrue(self.table.has_field('col1'))
        self.assertRaises(NoSuchFieldError, self.table.has_field, 'col4')

    def test_empty_table(self):
        args = ('table', [])
        self.assertRaises(TableHasNoFields, Table, *args)

    def test_table_verbose_names(self):
        vn = self.table.get_verbose_names()
        expected = ['"table1"."col1"', '"table1"."col2"', '"table1"."col3"']
        self.assertEqual(vn, expected)

    def test_table_verbose_names_no_enquote(self):
        vn = self.table_no_enquote.get_verbose_names()
        expected = ['table1.col1', 'table1.col2', 'table1.col3']
        self.assertEqual(vn, expected)

    def test_table_select(self):
        self.assertIsInstance(self.table.select(), SelectQuery)

    def test_select_query_str(self):
        select_query = self.query
        expected = 'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1'
        self.assertEqual(str(select_query), expected)

    def test_select_query_join(self):
        join = self.table.columns.col1 == self.table2.columns.col2
        select_query = self.query
        select_query.join(join)

        expected = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3", ',
            '"table2"."col1", "table2"."col2", "table2"."col3" FROM table1 ',
            'INNER JOIN "table2" ON "table1"."col1" = "table2"."col2"'
        ])
        self.assertEqual(str(select_query).rstrip(), expected)

    def test_select_query_filter(self):
        f = GtFilter('"table1"."col1"', 100, '%s')
        select_query = self.query
        select_query.where(f)
        q, params = select_query.str_and_params()

        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 ',
            'WHERE "table1"."col1" > %s'
        ])
        self.assertEqual(q, expected_text)
        self.assertEqual(params, [100])

    def test_select_query_complex_filter(self):
        f1 = GtFilter('"table1"."col1"', 100, '%s')
        f2 = LtFilter('"table1"."col1"', 200, '%s')
        complex_fitler = Q(f1, f2)
        select_query = self.query
        select_query.where(complex_fitler)
        q, params = select_query.str_and_params()

        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 ',
            'WHERE ("table1"."col1" > %s AND "table1"."col1" < %s)'
        ])
        self.assertEqual(q, expected_text)
        self.assertEqual(params, [100, 200])

    def test_select_query_limit(self):
        select_query = self.query
        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 LIMIT 10',
        ])
        with self.subTest():
            for n in [10, '10', 10.5]:
                select_query.limit(n)
                self.assertEqual(str(select_query), expected_text)

    def test_select_query_order_by(self):
        select_query = self.query
        select_query.order_by((['"table1"."col1"'], 'asc'))

        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 ',
            'ORDER BY "table1"."col1" ASC'
        ])
        self.assertEqual(str(select_query), expected_text)
        self.assertRaises(
            NoSuchFieldError,
            select_query.order_by,
            (['"table1"."col4"'], 'asc')
        )

    def test_empty_q_filter(self):
        q1 = Q()
        self.assertTrue(q1.is_empty)

        gt = GtFilter('"table1"."col1"', 100, '%s')
        q2 = Q(gt)
        expected_text = '"table1"."col1" > %s'
        self.assertEqual(str(q2), expected_text)

    def test_q_filter(self):
        def _test_or():
            Q() | 1
        self.assertRaises(TypeError, _test_or)

        gt = GtFilter('"table1"."col1"', 100, '%s')
        lt = LtFilter('"table1"."col1"', 200, '%s')
        q = Q(gt, lt)
        expected_text = '("table1"."col1" > %s AND "table1"."col1" < %s)'
        self.assertEqual(str(q), expected_text)

        q = Q(gt) | Q(lt)
        expected_text = '("table1"."col1" > %s OR "table1"."col1" < %s)'
        self.assertEqual(str(q), expected_text)


class TestQueryPreparation(NoofaTest):
    """
    Тестирование подготовки к построению запроса из json.
    """
    def setUp(self):
        self.base_query = {
            'base': 'table1',
            'tables': ['table1'],
        }
        self._subq = {
            'filters': [
                {
                    'is_complex': False, 'table': 'table1', 'field': 'f1', 'op': 'in', 'value': {
                        'is_subquery': True, 'base': 'table1', 'tables': ['table1'],
                        'values': [{'table': 'table1', 'field': 'f1'}],
                    }
                }
            ]
        }
        self._subq_another_table = {
            'filters': [
                {
                    'is_complex': False, 'table': 'table1', 'field': 'f1', 'op': 'in', 'value': {
                        'is_subquery': True, 'base': 'table2', 'tables': ['table2'],
                        'values': [{'table': 'table2', 'field': 'f2'}],
                    }
                }
            ]
        }
        self.with_subquery = {
            **self.base_query,
            **self._subq,
        }

    def test_no_subqueries(self):
        sq = utils._find_subqueries(self.base_query)
        sq_len = len(sq)
        self.assertEqual(sq_len, 0)

    def test_find_subqueries(self):
        sq = utils._find_subqueries(self.with_subquery)
        sq_len = len(sq)
        self.assertEqual(sq_len, 1)

    def test_find_tables(self):
        queries = utils._find_subqueries({**self.base_query, **self._subq_another_table})
        tables = utils._find_tables(queries)
        self.assertEqual(tables, ['table2'])

    def test_collect_tables(self):
        _ = {'base': 'table1', 'tables': ['table1', 'table3', 'table4']}
        tables = utils.collect_tables({**_, **self._subq_another_table})
        self.assertCountEqual(['table1', 'table2', 'table3', 'table4'], tables)


class TestQueryBuild(NoofaTest):
    """
    Тестирование построения запроса из json.
    """
    def setUp(self):
        self.maxDiff = None
        self.simple_json_query = {
            'base': 'table1',
            'tables': ['table1'],
        }
        self.values_simple = {
            'values': [{'table': 'table1', 'field': 'col1'}]
        }
        self.joins = {
            'joins': [
                {'l': 'table1', 'r': 'table2', 'j': 'inner',
                    'on': {'l': 'col1', 'r': 'col2'}},
                {'l': 'table1', 'r': 'table2', 'j': 'left',
                    'on': {'l': 'col2', 'r': 'col3'}},
                {'l': 'table1', 'r': 'table2', 'j': 'right',
                    'on': {'l': 'col3', 'r': 'col1'}},
            ]
        }
        self.limit = {'limit': 100}
        self.simple_filter = {
            'filters': [
                {'is_complex': False, 'table': 'table1', 'field': 'col1', 'op': '>', 'value': 100},
            ],
        }
        self.complex_filter = {
            'filters': [
                {'is_complex': True, 'op': 'and', 'filters': [
                    {'is_complex': False, 'table': 'table1', 'field': 'col1', 'op': '>', 'value': 100},
                    {'is_complex': False, 'table': 'table1', 'field': 'col1', 'op': '<', 'value': 200},
                ]},
            ],
        }
        self.orderby = {
            'order_by': [
                {'table': 'table1', 'fields': ['col1'], 'type': 'asc'},
            ],
        }
        self.mock_table1 = Table(
            'table1',
            ['col1', 'col2', 'col3'],
            enquote=True
        )
        self.mock_table2 = Table(
            'table2',
            ['col1', 'col2', 'col3'],
            enquote=True
        )

    def test_simple_select(self):
        qb = utils.Qbuilder(self.mock_tables, self.simple_json_query)
        query = qb.parse_query()
        expected_text = 'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1'
        self.assertEqual(str(query), expected_text)

    def test_select_list(self):
        qb = utils.Qbuilder(self.mock_tables,
            {**self.simple_json_query, **self.values_simple})
        query = qb.parse_query()
        expected_text = 'SELECT "table1"."col1" FROM table1'
        self.assertEqual(str(query), expected_text)

    def test_join(self):
        qb = utils.Qbuilder(self.mock_tables,
            {**self.simple_json_query, **self.joins})
        query = qb.parse_query()
        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3",',
            ' "table2"."col1", "table2"."col2", "table2"."col3" ',
            'FROM table1 INNER JOIN "table2" ON "table1"."col1" = "table2"."col2" ',
            'LEFT OUTER JOIN "table2" ON "table1"."col2" = "table2"."col3" ',
            'RIGHT OUTER JOIN "table2" ON "table1"."col3" = "table2"."col1"'
        ])
        self.assertEqual(str(query), expected_text)

    def test_simple_filter(self):
        qb = utils.Qbuilder(
            self.mock_tables,
            {**self.simple_json_query, **self.simple_filter},
            param_placeholder='%s'
        )
        query = qb.parse_query()
        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 ',
            'WHERE "table1"."col1" > %s'
        ])
        q, params = query.str_and_params()
        self.assertEqual(q, expected_text)
        self.assertEqual(params, [100, ])

    def test_complex_filter(self):
        qb = utils.Qbuilder(
            self.mock_tables,
            {**self.simple_json_query, **self.complex_filter},
            param_placeholder='%s'
        )
        query = qb.parse_query()
        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 ',
            'WHERE ("table1"."col1" > %s AND "table1"."col1" < %s)'
        ])
        q, params = query.str_and_params()
        self.assertEqual(q, expected_text)
        self.assertEqual(params, [100, 200])

    def test_limit(self):
        qb = utils.Qbuilder(self.mock_tables,
            {**self.simple_json_query, **self.limit})
        query = qb.parse_query()
        expected_text = 'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 LIMIT 100'
        self.assertEqual(str(query), expected_text)

    def test_limit_mssql(self):
        qb = utils.Qbuilder(self.mock_tables,
            {**self.simple_json_query, **self.limit},
            mssql=True,
        )
        query = qb.parse_query()
        expected_text = 'SELECT TOP 100 "table1"."col1", "table1"."col2", "table1"."col3" FROM table1'
        self.assertEqual(str(query), expected_text)

    def test_orderby(self):
        qb = utils.Qbuilder(self.mock_tables,
            {**self.simple_json_query, **self.orderby})
        query = qb.parse_query()
        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2", "table1"."col3" FROM table1 ',
            'ORDER BY "table1"."col1" ASC'
        ])
        self.assertEqual(str(query), expected_text)

    @property
    def mock_tables(self):
        mt = {}
        for table in [self.mock_table1, self.mock_table2]:
            mt[table._name] = table
        return mt


class TestQueryFilters(NoofaTest):
    """
    Тестирование классов фильтров запросов.
    """
    @classmethod
    def setUpClass(cls):
        cls.wildcard = '%s'
        cls.col = 'col'
        cls.value = 10
        cls.comparison_template = f'{cls.col} %s %{cls.wildcard}'
        cls.args = (
            cls.col,
            cls.value,
            cls.wildcard
        )

    def test_eq(self):
        f = EqFilter(*self.args)
        self.assertEqual(str(f), self.comparison_template % '=')

    def test_neq(self):
        f = NeqFilter(*self.args)
        self.assertEqual(str(f), self.comparison_template % '<>')

    def test_gt(self):
        f = GtFilter(*self.args)
        self.assertEqual(str(f), self.comparison_template % '>')

    def test_ge(self):
        f = GeFilter(*self.args)
        self.assertEqual(str(f), self.comparison_template % '>=')

    def test_lt(self):
        f = LtFilter(*self.args)
        self.assertEqual(str(f), self.comparison_template % '<')

    def test_le(self):
        f = LeFilter(*self.args)
        self.assertEqual(str(f), self.comparison_template % '<=')

    def test_contains(self):
        f = ContainsFilter(*self.args)
        self.assertEqual(str(f), f'{self.col} LIKE {self.wildcard}')
        self.assertEqual(f._params, [f'%{self.value}%'])

    def test_startswith(self):
        f = StartsWithFilter(*self.args)
        self.assertEqual(str(f), f'{self.col} LIKE {self.wildcard}')
        self.assertEqual(f._params, [f'{self.value}%'])

    def test_endswith(self):
        f = EndsWithFilter(*self.args)
        self.assertEqual(str(f), f'{self.col} LIKE {self.wildcard}')
        self.assertEqual(f._params, [f'%{self.value}'])

    def test_in(self):
        f = InFilter(self.col, [1, 2], self.wildcard)
        self.assertEqual(str(f), 'col IN (%s, %s)')
        self._params = [1, 2]

    def test_not_in(self):
        f = NotInFilter(self.col, [1, 2], self.wildcard)
        self.assertEqual(str(f), 'col NOT IN (%s, %s)')
        self._params = [1, 2]
