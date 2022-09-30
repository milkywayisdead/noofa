"""
Классы графических компонентов отчёта.
"""
import plotly.express as px
import plotly.graph_objects as go

from ..core.dataframes.panda_builder import pd


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
        build_from, base_value = base.pop('from'), base.pop('value')

        #  необязательный параметр, определяющий объект "вычислителя"
        using_evaluator = options.get('using_evaluator', None)

        self._tables[table_id] = ReportTable(
            id=table_id, type='table',
            build_from=build_from, base_value=base_value,
            evaluator=using_evaluator,
            **options,
        )

    def add_figure(self, **options):
        options.pop('type') if 'type' in options else 0
        figure_id = options.pop('id')
        base = options.pop('base')
        build_from, base_value = base['from'], base['value']
        using_evaluator = options.get('using_evaluator', None)
        options.update({
            'x': base.get('x', ''),
            'y': base.get('y', ''),
            'values': base.get('values', ''),
            'names': base.get('names', ''),
            'line_group': base.get('line_group', ''),
            'barmode': base.get('barmode', ''),
            'labels': base.get('labels', ''),
        })

        engine = options.get('engine', 'plotly')
        figure_type = options['figure_type']
        base_cls = FIGURES[engine][figure_type]
        self._figures[figure_id] = base_cls(
            id=figure_id, type='figure',
            build_from=build_from, base_value=base_value,
            evaluator=using_evaluator,
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
    """
    Базовый класс для компонентов отчёта.
    """
    def __init__(self, **options):
        self.id = options['id']
        self.type = options['type']  # chart, table
        self._build_from = options['build_from']
        self._base = options['base_value']
        self.title_text = options.get('title_text', '')
        self._title_font_size = options.get('title_font_size', 12)

        #  "вычислитель" - объект, который будет вычислять результаты
        #  в случае, когда base либо её части строятся из выражения ('expression');
        #  этим объектом на данный момент должен быть экз. ReportBuilder из noofa.builder.
        self._evaluator = options.get('evaluator', None)

    @property
    def evaluator(self):
        return self._evaluator

    @evaluator.setter
    def evaluator(self, value):
        self._evaluator = value

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
    Компонент-таблица.
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
        self.df = self.evaluator.evaluate(self.base)

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
        file = open(path, 'w')
        return self.df.to_csv(file, sep=sep, index=idx)

    def to_excel(self, path):
        return self.df.to_excel(path) if self.df is not None else None

    @property
    def header(self):
        """
        Список наименований столбцов таблицы.
        """
        return self.df.columns.to_list()

    @property
    def body(self):
        """
        Список списков значений соотв. строк таблицы.
        """
        recs = list(self.df.to_records(index=False))
        return [list(r) for r in recs]

    @property
    def data(self):
        """
        Список списков значений ячеек таблицы, включая заголовок.
        """
        data = [self.header]
        for r in self.body:
            data.append(r)
        return data


class ReportFigure(ReportComponent):
    """
    Базовый компонент-график. Не должен использоваться 
    при создании компонентов. Компоненты создаются по
    экземплярам наследуемых классов, в которых должен быть реализован
    метод build - метод построения графика.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self._showlegend = options.get('showlegend', False)
        self._figure = None
        self._names = options.get('names', '')
        self._values = options.get('values', '')
        self._line_group = options.get('line_group', '')
        self._x_col, self._y_col = options.get('x', ''), options.get('y', '')
        self._barmode = options.get('barmode', '')
        self._labels = options.get('labels', '')

    @property
    def figure(self):
        return self._figure

    def build(self):
        """
        Построение графика.
        """
        pass

    def to_bytes(self):
        """
        График в виде байт.
        График должен быть предварительно построен
        при помощи метода build.
        """
        return self.figure.to_image()

    def _update_layout(self):
        """
        Обновление компоновки/оформления графика.
        """
        self.figure.update_layout(
            showlegend=self._showlegend,
            title_text=self.title_text,
            title_font_size=self._title_font_size,
        )

    def _eval_xy(self, from_, value):
        """
        Получение значений для осей x либо y по значениям параметров конфиги.
        Используется при построении линейных графиков и столбчатых диаграмм.
        """
        evaluator = self.evaluator
        if from_ == 'expression':
            res = evaluator.evaluate(value)
        elif from_ == 'column':
            df_str, col_name, df_from = value['dataframe'], value['column'], value['df_from']
            if df_from == 'expression':
                _df = evaluator.evaluate(df_str)
            else:
                _df = evaluator.get_or_build_dataframe(df_str)
            res = _df[col_name]
        return res


class PlotlyMixin:
    """
    Доп. класс для компонентов-графиков plotly, при наследовании указывающий, что компонент 
    является графиком на базе plotly, и реализующий методы
    отображения данных по графику в виде словаря и сохранения в файл.
    """
    @property
    def engine(self):
        return 'plotly'

    def to_dict(self):
        return self.figure.to_dict()

    def to_png(self, path):
        if not path.endswith('.png'):
            path += '.png'
        self.figure.write_image(path)


class PlotlyLine(ReportFigure, PlotlyMixin):
    """
    График с линиями с использованием plotly.
    """
    def build(self):
        base, build_from = self.base, self.build_from
        data, fig = [], px.line()
        evaluator = self.evaluator
        if build_from == 'list':
            for i in base:
                x_from, y_from = i['x_from'], i['y_from']
                _x, _y = i['x'], i['y']
                x, y = self._eval_xy(x_from, _x), self._eval_xy(y_from, _y)
                data.append({
                    'x': x,
                    'y': y,
                    'name': i['name'],
                })
            fig = px.line()
            for d in data:
                x, y, name = d['x'], d['y'], d['name']
                x, y = _to_list(x), _to_list(y)
                fig.add_trace(go.Scatter(x=x, y=y, name=name))
        elif build_from == 'dataframe':
            df = evaluator.evaluate(base['dataframe'])
            fig = px.line(df, x=self._x_col, y=self._y_col)
        elif build_from == 'grouped':
            df_from, df_str = base['df_from'], base['dataframe']
            if df_from == 'expression':
                df = evaluator.evaluate(df_str)
            else:
                df = evaluator.get_or_build_dataframe(df_str)
            fig = px.line(
                df,
                x=self._x_col, y=self._y_col, 
                line_group=self._line_group, color=self._line_group,
            )
        self._figure = fig
        self._update_layout()
        return self.figure


class PlotlyPie(ReportFigure, PlotlyMixin):
    """
    Круговая диаграмма с использованием plotly.
    """
    def build(self):
        base, build_from = self.base, self.build_from
        fig = px.pie()
        evaluator = self.evaluator
        if build_from == 'list':
            values, names = [], []
            for i in base:
                value = evaluator.evaluate(i['value'])
                values.append(value)
                names.append(i['name'])
            fig = px.pie(values=values, names=names)
        elif build_from == 'dataframe':
            df = base['dataframe']
            df = evaluator.evaluate(df)
            values, names = self._values, self._names
            fig = px.pie(df, values=values, names=names)
        self._figure = fig
        self._update_layout()
        return self.figure


class PlotlyBar(ReportFigure, PlotlyMixin):
    """
    Столбчатая диаграмма с использованием plotly.
    """
    _orientation = 'h'

    @property
    def orientation(self):
        return self.__class__._orientation

    def build(self):
        base, build_from = self.base, self.build_from
        orientation, barmode = self.orientation, self._barmode
        if build_from == 'list':
            data, fig = [], px.bar(orientation=orientation)
            for i in base:
                x_from, y_from = i['x_from'], i['y_from']
                _x, _y = i['x'], i['y']
                x, y = self._eval_xy(x_from, _x), self._eval_xy(y_from, _y)
                data.append({
                    'x': x,
                    'y': y,
                    'name': i['name'],
                })
            for d in data:
                x, y = _to_list(d['x']), _to_list(d['y'])
                fig.add_trace(go.Bar(x=x, y=y, name=d['name']))
        elif build_from == 'dataframe':
            df_str, x_col, y_col = base['dataframe'], self._x_col, self._y_col
            df = self.evaluator.evaluate(df_str)
            fig = px.bar(df, x=x_col, y=y_col, orientation=orientation)

        self._figure = fig
        fig.update_layout(barmode=barmode)
        self._update_layout()
        return self.figure


class PlotlyHbar(PlotlyBar, PlotlyMixin):
    _orientation = 'v'


FIGURES = {
    'plotly': {
        'line': PlotlyLine,
        'pie': PlotlyPie,
        'bar': PlotlyBar,
        'hbar': PlotlyHbar,
    },
}


def _to_list(data):
    """
    Преобразование pandas.Series и датафреймов pandas,
    содержащих один столбец, в list.
    """
    if isinstance(data, list):
        return data
    elif isinstance(data, pd.Series):
        return data.to_list()
    elif isinstance(data, pd.DataFrame):
        cols = data.columns
        if len(cols) == 1:
            return data[cols[0]].to_list()
    return []