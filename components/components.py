from .exceptions import SchemaComponentNotFound
from .tables import ReportTable, ReportPivotTable
from .figures import FIGURES


class ComponentsSchema:
    """
    Схема компонентов отчёта.
    Содержит словари с таблицами и графиками.
    """
    def __init__(self, dataframes=None, tables=None, figures=None, **kwargs):
        self._dataframes = dataframes or {}
        self._tables = tables or {}
        self._figures = figures or {}

    def add_table(self, id=None, base=None, using_evaluator=None, **options):
        build_from, base_value = base.pop('from'), base.pop('value')

        self._tables[id] = ReportTable(
            id=id,
            build_from=build_from,
            base_value=base_value,
            evaluator=using_evaluator,
            **options,
        )

    def add_pivot_table(self, id=None, base=None, pivot_conf=None,
        using_evaluator=None, **options):
        build_from, base_value = base.pop('from'), base.pop('value')

        self._tables[id] = ReportPivotTable(
            id=id,
            build_from=build_from,
            base_value=base_value,
            pivot_conf=pivot_conf,
            evaluator=using_evaluator,
            **options,
        )

    def add_figure(self, id=None, base=None, using_evaluator=None, engine='plotly',
        figure_type=None, **options):
        build_from, base_value = base['from'], base['value']
        options.update({
            'x': base.get('x', ''),
            'y': base.get('y', ''),
            'values': base.get('values', ''),
            'names': base.get('names', ''),
            'line_group': base.get('line_group', ''),
            'barmode': base.get('barmode', ''),
            'labels': base.get('labels', ''),
        })

        base_cls = FIGURES[engine][figure_type]
        self._figures[id] = base_cls(
            id=id,
            build_from=build_from,
            base_value=base_value,
            evaluator=using_evaluator,
            **options,
        )

    def get_component(self, component_id):
        try:
            return self.get_table(component_id)
        except SchemaComponentNotFound:
            try:
                return self.get_figure(component_id)
            except:
                raise SchemaComponentNotFound(component_id, '_')

    def get_table(self, table_id):
        table = self._tables.get(table_id, None)
        if table is None:
            raise SchemaComponentNotFound(table_id, 'table')
        return table

    def get_figure(self, figure_id):
        figure = self._figures.get(figure_id, None)
        if figure is None:
            raise SchemaComponentNotFound(figure_id, 'figure')
        return figure
