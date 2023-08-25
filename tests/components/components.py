from pandas import DataFrame
from unittest.mock import Mock

from noofa.tests.base import NoofaTest
from noofa.components.components import ComponentsSchema
from noofa.components.exceptions import SchemaComponentNotFound
from noofa.components.tables import ReportTable, ReportPivotTable
from noofa.components.figures import PlotlyLine


class TestComponentsSchema(NoofaTest):
    """
    Тестирование схемы компонентов.
    """
    @classmethod
    def setUpClass(cls):
        cls.evaluator = _mock_evaluator

    def setUp(self):
        self.schema = ComponentsSchema()

        self.table_conf = {
            'id': 'table1',
            'base': {
                'from': 'dataframe',
                'value': 'df1',
            },
            'title_text': 'Table',
            'using_evaluator': self.evaluator,
            'aliases': {'b': 'B'},
            'exclude': ['c'],
        }
        self.pivot_table_conf = {
            'id': 'pivottable1',
            'base': {
                'from': 'dataframe',
                'value': 'df1',
            },
            'title_text': 'Pivot table',
            'using_evaluator': self.evaluator,
            'pivot_conf': {
                'index': ['d'],
                'columns': [],
                'aggfunc': {'c': ['sum']},
                'values': {},
                'fill_value': None,
            },
        }
        self.figures_conf = _figures_conf

    def test_add_table(self):
        self.assertRaises(SchemaComponentNotFound, self.schema.get_table, 'table1')
        n1 = len(self.schema._tables.keys())
        self.schema.add_table(**self.table_conf)
        n2 = len(self.schema._tables.keys())
        self.assertEqual(n1 + 1, n2)

        table = self.schema.get_table('table1')
        self.assertIsInstance(table, ReportTable)

    def test_add_pivot_table(self):
        self.assertRaises(SchemaComponentNotFound, self.schema.get_table, 'pivottable1')
        n1 = len(self.schema._tables.keys())
        self.schema.add_pivot_table(**self.pivot_table_conf)
        n2 = len(self.schema._tables.keys())
        self.assertEqual(n1 + 1, n2)

        pt = self.schema.get_table('pivottable1')
        self.assertIsInstance(pt, ReportPivotTable)

    def test_add_figure(self):
        self.assertRaises(SchemaComponentNotFound, self.schema.get_figure, 'fig1')
        n1 = len(self.schema._figures.keys())
        self.schema.add_figure(**self.figures_conf['fig1'])
        n2 = len(self.schema._figures.keys())
        self.assertEqual(n1 + 1, n2)

        fig = self.schema.get_figure('fig1')
        self.assertIsInstance(fig, PlotlyLine)

    def test_table(self):
        self.schema.add_table(**self.table_conf)
        table = self.schema.get_table('table1')
        table.build()
        df = table.df
        self.assertIn('a', df)
        self.assertNotIn('b', df)
        self.assertIn('B', df)
        self.assertNotIn('c', df)

    def test_pivot_table(self):
        self.schema.add_pivot_table(**self.pivot_table_conf)
        pt = self.schema.get_table('pivottable1')
        pt.build()
        df = pt.pivot_df
        self.assertCountEqual(list(df['c']), [21, 10, 11])

    def test_build_lines_and_bars(self):
        for f, conf in self.figures_conf.items():
            self.schema.add_figure(**conf)
            fig = self.schema.get_figure(f)

            success = True
            try:
                fig.build()
            except:
                success = False

            with self.subTest(f):
                self.assertTrue(success)


_mock_evaluator = Mock()
_df = DataFrame({
    'a': [1, 2, 3, 4],
    'b': [5, 6, 7, 8],
    'c': [9, 10, 11, 12],
    'd': ['a', 'b', 'c', 'a'],
})
_mock_evaluator.evaluate.return_value = _df
_mock_evaluator.get_or_build_dataframe.return_value = _df

_pie_mock_evaluator = Mock()
_pie_mock_evaluator.get_or_build_dataframe.return_value = _df
_pie_mock_evaluator.evaluate.return_value = 1

_figures_conf = {
    'fig1': {
        'id': 'fig1',
        'base': {
            'from': 'dataframe',
            'value': {'dataframe': 'df1'},
            'x': 'a',
            'y': 'b',
        },
        'figure_type': 'line',
        'using_evaluator': _mock_evaluator,
    },
    'line1': {
        'id': 'line1',
        'base': {
            'from': 'grouped',
            'value': {'df_from': 'expression', 'dataframe': 'df1'},
            'x': 'a',
            'y': 'b',
            'line_group': 'd',
        },
        'figure_type': 'line',
        'using_evaluator': _mock_evaluator,
    },
    'line2': {
        'id': 'line2',
        'base': {
            'from': 'grouped',
            'value': {'df_from': 'dataframe', 'dataframe': 'df1'},
            'x': 'a',
            'y': 'b',
            'line_group': 'd',
        },
        'figure_type': 'line',
        'using_evaluator': _mock_evaluator,
    },
    'line3': {
        'id': 'line3',
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
        'using_evaluator': _mock_evaluator,
    },
    'line4': {
        'id': 'line4',
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
        'using_evaluator': _mock_evaluator,
    },
    'bar1': {
        'id': 'bar1',
        'base': {
            'from': 'dataframe',
            'value': {'dataframe': 'df1'},
            'x': 'a',
            'y': 'b',
            'barmode': 'stack',
        },
        'figure_type': 'bar',
        'using_evaluator': _mock_evaluator,
    },
    'bar2': {
        'id': 'bar2',
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
        'using_evaluator': _mock_evaluator,
    },
    'bar3': {
        'id': 'bar3',
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
        'using_evaluator': _mock_evaluator,
    },
    'pie1': {
        'id': 'pie1',
        'base': {
            'from': 'dataframe',
            'value': {
                'dataframe': 'df1',
            },
            'names': 'd',
            'values': 'a',
        },
        'figure_type': 'pie',
        'using_evaluator': _mock_evaluator,
    },
    'pie2': {
        'id': 'pie2',
        'base': {
            'from': 'list',
            'value': [
                {'name': 'a1', 'value': 'some_expression'},
                {'name': 'a2', 'value': 'some_other_expression'},
            ],
        },
        'figure_type': 'pie',
        'using_evaluator': _pie_mock_evaluator,
    },
    'pie3': {
        'id': 'pie3',
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
        'using_evaluator': _pie_mock_evaluator,
    },
}
