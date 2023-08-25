from noofa.tests.base import NoofaTest
from noofa.builders.builders import ReportBuilder


class TestBuilder(NoofaTest):
    """
    Тесты формирователя отчётов.
    """
    def setUp(self):
        self.sources = _sources_conf()
        self.queries = _queries_conf()
        self.dataframes = _dataframes_conf()
        self.tables = _tables_conf()
        self.figures = _figures_conf()
        self.conf = {
            'data_config': {
                'sources': self.sources,
                'queries': self.queries,
                'dataframes': self.dataframes,
            },
            'components_config': {**self.tables, **self.figures},
        }

    def test_init(self):
        success = True
        try:
            rb = ReportBuilder(**self.conf)
        except:
            success = False
        self.assertTrue(success)


def _sources_conf():
    return {
        'src1': {
            'id': 'src1',
            'type': 'postgres',
            'name': 'test_source',
            'from': 'json',
            'value': {
                'host': '',
                'port': 9999,
                'dbname': '',
                'user': '',
                'password': '',
            },
        },
        'src2': {
            'id': 'src2',
            'type': 'postgres',
            'name': 'test_source2',
            'from': 'conn_str',
            'value': 'host=1;port=1;dbname=1;user=1;password=1',
        },
    }

def _queries_conf():
    return {
        'q1': {
            'id': 'q1',
            'name': 'test_query1',
            'from': 'json',
            'source': 'src1',
            'value': {
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
            'from': 'expression',
            'source': 'src1',
            'value': 'sql_select("a")',
        },
    }

def _dataframes_conf():
    return {
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

def _tables_conf():
    return {
        'table1': {
            'id': 'table1',
            'type': 'table',
            'base': {
                'from': 'dataframe',
                'value': 'df1',
            },
            'title_text': 'Table',
            'aliases': {'b': 'B'},
            'exclude': ['c'],
        },
        'pivottable1': {
            'id': 'pivottable1',
            'type': 'pivot_table',
            'base': {
                'from': 'dataframe',
                'value': 'df1',
            },
            'title_text': 'Pivot table',
            'pivot_conf': {
                'index': ['d'],
                'columns': [],
                'aggfunc': {'c': ['sum']},
                'values': {},
                'fill_value': None,
            },
        },
    }

def _figures_conf():
    return {
        'fig1': {
            'id': 'fig1',
            'type': 'figure',
            'base': {
                'from': 'dataframe',
                'value': {'dataframe': 'df1'},
                'x': 'a',
                'y': 'b',
            },
            'figure_type': 'line',
        },
        'line1': {
            'id': 'line1',
            'type': 'figure',
            'base': {
                'from': 'grouped',
                'value': {'df_from': 'expression', 'dataframe': 'df1'},
                'x': 'a',
                'y': 'b',
                'line_group': 'd',
            },
            'figure_type': 'line',
        },
        'line2': {
            'id': 'line2',
            'type': 'figure',
            'base': {
                'from': 'grouped',
                'value': {'df_from': 'dataframe', 'dataframe': 'df1'},
                'x': 'a',
                'y': 'b',
                'line_group': 'd',
            },
            'figure_type': 'line',
        },
        'line3': {
            'id': 'line3',
            'type': 'figure',
            'base': {
                'from': 'list',
                'value': [
                    {
                        'name': 'l1',
                        'x_from': 'expression',
                        'y_from': 'expression',
                        'x': 'df1',
                        'y': 'df1',
                    },
                ],
            },
            'figure_type': 'line',
        },
        'line4': {
            'id': 'line4',
            'type': 'figure',
            'base': {
                'from': 'list',
                'value': [
                    {
                        'name': 'l1',
                        'x_from': 'column',
                        'y_from': 'column',
                        'x': {'df_from': 'expression', 'dataframe': 'df1', 'column': 'a'},
                        'y': {'df_from': 'dataframe', 'dataframe': 'df1', 'column': 'b'},
                    },
                ],
            },
            'figure_type': 'line',
        },
        'bar1': {
            'id': 'bar1',
            'type': 'figure',
            'base': {
                'from': 'dataframe',
                'value': {'dataframe': 'df1'},
                'x': 'a',
                'y': 'b',
                'barmode': 'stack',
            },
            'figure_type': 'bar',
        },
        'bar2': {
            'id': 'bar2',
            'type': 'figure',
            'base': {
                'from': 'list',
                'value': [
                    {
                        'name': 'b1',
                        'x_from': 'column',
                        'y_from': 'column',
                        'x': {'df_from': 'expression', 'dataframe': 'df1', 'column': 'a'},
                        'y': {'df_from': 'dataframe', 'dataframe': 'df1', 'column': 'b'},
                    },
                ],
                'barmode': 'stack',
            },
            'figure_type': 'bar',
        },
        'bar3': {
            'id': 'bar3',
            'type': 'figure',
            'base': {
                'from': 'agg',
                'value': {
                    'dataframe': 'anything',
                    'groupby': ['d'],
                    'func': 'sum',
                    'on': 'a',
                },
                'barmode': 'stack',
            },
            'figure_type': 'bar',
        },
        'pie1': {
            'id': 'pie1',
            'type': 'figure',
            'base': {
                'from': 'dataframe',
                'value': {
                    'dataframe': 'df1',
                },
                'names': 'd',
                'values': 'a',
            },
            'figure_type': 'pie',
        },
        'pie2': {
            'id': 'pie2',
            'type': 'figure',
            'base': {
                'from': 'list',
                'value': [
                    {'name': 'a1', 'value': 'some_expression'},
                    {'name': 'a2', 'value': 'some_other_expression'},
                ],
            },
            'figure_type': 'pie',
        },
        'pie3': {
            'id': 'pie3',
            'type': 'figure',
            'base': {
                'from': 'agg',
                'value': {
                    'dataframe': 'anything',
                    'groupby': ['d'],
                    'func': 'sum',
                    'on': 'a',
                },
            },
            'figure_type': 'pie',
        },
    }
