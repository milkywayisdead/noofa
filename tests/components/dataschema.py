from unittest.mock import patch, Mock

from noofa.core.sources.query import Table
from noofa.components.dataschema import (
    DataSchema,
    SchemaSource,
    SchemaQuery,
    SchemaDataframe
)
from noofa.tests.base import NoofaTest
from noofa.components.exceptions import SchemaComponentNotFound


class TestDataschema(NoofaTest):
    """
    Тестирование схемы данных.
    """
    @classmethod
    def setUpClass(cls):
        cls.sources = {
            'src1': {
                'id': 'src1',
                'type': 'postgres',
                'name': 'test_source',
            },
        }
        cls.queries = {
            'q1': {
                'id': 'q1',
                'name': 'test_query1',
                'build_from': 'json',
                'source': 'src1',
                'query_src': {
                    'base': 'table1',
                    'tables': ['table1'],
                    'filters': [
                        {
                            'is_complex': False,
                            'table': 'table1',
                            'field': 'col1',
                            'op': '>',
                            'value': 1,
                        }
                    ],
                },
            },
            'q2': {
                'id': 'q2',
                'name': 'test_query2',
                'build_from': 'expression',
                'source': 'src1',
                'query_src': 'sql_select("a")',
            },
            'q3': {
                'id': 'q3',
                'name': 'test_query3',
                'build_from': 'expression',
                'source': 'src2',
                'query_src': 'sql_select("a")',
            },
        }
        cls.dataframes = {
            'df1': {
                'id': 'df1',
                'name': 'test_df1',
                'base': {
                    'type': 'query',
                    'source': 'src1',
                    'value': 'q1',
                },
            },
            'df2': {
                'id': 'df2',
                'name': 'test_df2',
                'base': {
                    'type': 'source',
                    'source': '',
                    'value': 'src1',
                },
            },
            'df3': {
                'id': 'df3',
                'name': 'test_df3',
                'base': {
                    'type': 'expression',
                    'value': 'dataframe()',
                },
            },
        }

    def setUp(self):
        self.ds = DataSchema()

    def test_add_source(self):
        ds = self.ds
        self.assertRaises(SchemaComponentNotFound, ds.get_source, 'src1')

        n1 = len(ds._sources.keys())
        ds.add_source(**self.sources['src1'])
        n2 = len(ds._sources.keys())
        self.assertEqual(n1 + 1, n2)

        src = ds.get_source('src1')
        self.assertIsInstance(src, SchemaSource)

    def test_add_query(self):
        ds = self.ds

        self.assertRaises(SchemaComponentNotFound, ds.get_query, 'q1')
        self.assertRaises(SchemaComponentNotFound, ds.get_query, 'q2')

        ds.add_source(**self.sources['src1'])
        n1 = len(ds._queries.keys())
        ds.add_query(**self.queries['q1'])
        ds.add_query(**self.queries['q2'])
        n2 = len(ds._queries.keys())
        self.assertEqual(n1 + 2, n2)

        src = ds.get_query('q1')
        self.assertIsInstance(src, SchemaQuery)

        with self.assertRaises(KeyError):
            ds.add_query(**self.queries['q3'])

    def test_add_dataframe(self):
        ds = self.ds

        self.assertRaises(SchemaComponentNotFound, ds.get_dataframe, 'df1')
        self.assertRaises(SchemaComponentNotFound, ds.get_dataframe, 'df2')
        self.assertRaises(SchemaComponentNotFound, ds.get_dataframe, 'df3')

        ds.add_source(**self.sources['src1'])
        ds.add_query(**self.queries['q1'])
        n1 = len(ds._dataframes.keys())
        ds.add_dataframe(**self.dataframes['df1'])
        ds.add_dataframe(**self.dataframes['df2'])
        ds.add_dataframe(**self.dataframes['df3'])
        n2 = len(ds._dataframes.keys())
        self.assertEqual(n1 + 3, n2)

        df_names = list(ds._dataframes_by_name.keys())
        self.assertCountEqual(df_names, ['test_df1', 'test_df2', 'test_df3'])

        df = ds.get_dataframe('df1')
        self.assertIsInstance(df, SchemaDataframe)

    @patch('noofa.components.dataschema.SchemaSource', autospec=True)
    def test_schema_query(self, mock_schema_source):
        mock_source = Mock()
        mock_source.is_opened = True
        mock_source.get_table_multiple.return_value = {
            'table1': Table('table1', ['col1', 'col2'], enquote=True),
        }
        mock_conn = Mock()
        mock_conn.source_type = 'postgres'
        mock_source.connection = mock_conn
        mock_source.wildcard = '%s'
        mock_schema_source.return_value = mock_source

        ds = self.ds
        ds.add_source(**self.sources['src1'])
        ds.add_query(**self.queries['q1'])
        q = ds.get_query('q1')
        q.query = q.query_src
        query_obj = q._compile()
        expected_text = ''.join([
            'SELECT "table1"."col1", "table1"."col2" FROM table1 ',
            'WHERE "table1"."col1" > %s'
        ])
        self.assertEqual((expected_text, [1]), query_obj.str_and_params())

        mock_conn.source_type = 'mssql'
        mock_source.wildcard = '?'
        expected_text = expected_text.replace('%s', '?')
        query_obj = q._compile()
        self.assertEqual((expected_text, [1]), query_obj.str_and_params())

    @patch('noofa.components.dataschema.SchemaQuery', autospec=True)
    def test_schema_dataframe(self, mock_query):
        mock_data = Mock()
        mock_data.columns = ['a', 'b', 'c']
        mock_data.data = [(1, 2 ,3), (4, 5, 6)]
        mock_query.return_value.execute.return_value = mock_data

        ds = self.ds
        ds.add_source(**self.sources['src1'])
        ds.add_query(**self.queries['q1'])
        ds.add_dataframe(**self.dataframes['df1'])
        schema_df = ds.get_dataframe('df1')

        data = schema_df.get_data()
        self.assertTrue(hasattr(data, 'columns'))
        self.assertTrue(hasattr(data, 'data'))

        df = schema_df.build()
        self.assertEqual(df.shape, (2, 3))
        self.assertCountEqual(['a', 'b', 'c'], list(df.columns))
