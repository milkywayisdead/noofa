"""
Классы графических компонентов отчёта.
"""
from .graph import FIGURES


class ComponentsSchema:
    """
    Схема компонентов отчёта.
    Содержит словари с таблицами и графиками.
    """
    def __init__(self, dataframes={}, **kwargs):
        self._dataframes = dataframes
        self._tables = kwargs.get('tables', {})
        self._figures = kwargs.get('figures', {})

    def add_table(self, **options):
        options.pop('type') if 'type' in options else 0
        table_id = options.pop('id')
        base = options.pop('base')
        build_from, base_value = base.pop('from'), base.pop('value'),
        self._tables[table_id] = ReportTable(
            id=table_id, type='table',
            build_from=build_from, base_value=base_value,
            **options,
        )

    def add_figure(self, **options):
        options.pop('type') if 'type' in options else 0
        figure_id = options.pop('id')
        base = options.pop('base')
        build_from, base_value = base['from'], base['value']
        engine = options.get('engine', 'plotly')
        if engine:
            options.pop('engine')
        self._figures[figure_id] = ReportFigure(
            id=figure_id, type='table',
            build_from=build_from, base_value=base_value,
            engine=engine,
            **options,
        )

    def get_component(self, component_id):
        try:
            return self.get_table(component_id)
        except KeyError:
            return self.get_figure(component_id)

    def get_table(self, table_id):
        return self._tables[table_id]

    def get_figure(self, figure_id):
        return self._figures[figure_id]


class ReportComponent:
    def __init__(self, **options):
        self.id = options['id']
        self.type = options['type']  # chart, table, filter
        self._build_from = options['build_from']
        self._base = options['base_value']
        title = options.get('title', {})
        self._title = title.get('text', '')
        self._title_font_size = title.get('font_size', 12)

    @property
    def build_from(self):
        """
        Формат, из которого строится основание для компонента.
        """
        return self._build_from

    @property
    def base(self):
        """
        Значение основания, из которого строится компонент.
        """
        return self._base


class ReportTable(ReportComponent):
    """
    Таблица в компонентах отчёта.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self._to_exclude = options.get('to_exclude', {})  # столбцы, которые исключ. при выводе

        # словарь для переименования выводимых столбцов;
        # должен иметь формат {название_существующего_столбца1: новое_название, ...}
        self._aliases = options.get('aliases', {})
        self._df = None  #  датафрейм, данные из которого будут выводиться в виде таблицы

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        self._df = value

    def build(self):
        """
        Построение таблицы. Под этим подразумевается переименование столбцов 
        и отбрасывание лишних столбцов в зависимости от конфигурации таблицы.
        """
        if self._df is not None:
            if self._aliases:
                self.df = self.df.rename(columns=self._aliases)

            cols = self._to_exclude
            if cols:
                if len(cols) < len(self.df.columns):
                    self.df = self.df.drop(cols, axis=1)
        return self

    def to_csv(self, path=None):
        sep, idx = ';', False
        if path is None:
            return self.df.to_csv(sep=sep, index=idx)
        file = open(path, 'a')
        return self.df.to_csv(file, sep=sep, index=idx)

    def to_excel(self, path):
        return self.df.to_excel(path) if self.df is not None else None

    @property
    def header(self):
        return self.df.columns.to_list()


class ReportFigure(ReportComponent):
    def __init__(self, **options):
        super().__init__(**options)
        self._engine = options['engine']
        self._figure_type = options['figure_type']
        self._base_figure = FIGURES[self._engine][self._figure_type]

    def add_dataset(self, dataset):
        pass

    def to_bytes(self):
        pass

    def to_png(self):
        pass