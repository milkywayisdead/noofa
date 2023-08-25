import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from .base import ReportComponent
from .mixins import PlotlyMixin
from ..core.dataframes.panda_builder import pd


class ReportFigure(ReportComponent):
    """
    Базовый компонент-график. Не должен использоваться
    при создании компонентов. Компоненты создаются по
    экземплярам наследуемых классов, в которых должен быть реализован
    метод build - метод построения графика.
    """
    def __init__(self, x='', y='', showlegend=False, names='', values='',
        barmode='stack', labels='', line_group='', **options):
        super().__init__(**options)
        self.type = 'figure'
        self._showlegend = showlegend
        self._figure = None
        self._names = names
        self._values = values
        self._line_group = line_group
        self._x_col, self._y_col = x, y
        self._barmode = barmode
        self._labels = labels

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
                color=self._line_group,
                line_group=self._line_group,
            )
        self._figure = fig
        self._update_layout()
        return self.figure


class PlotlyPie(ReportFigure, PlotlyMixin):
    """
    Круговая диаграмма с использованием plotly.
    """
    def using_agg(self, dataframe=None, groupby=[],
        on='', func='count', evaluator=None, **kwargs):
        df = evaluator.get_or_build_dataframe(dataframe)

        if groupby:
            agg_df = df.groupby(groupby).agg(func)
        else:
            agg_df = self._no_groupby(df, on, func)
            return px.pie(agg_df, names='index', values=func)

        names = list(agg_df.index)
        names_col = ', '.join(groupby)
        agg_df[names_col] = names
        agg_col_name = f'{func}({on})'
        agg_df[agg_col_name] = agg_df[on]

        agg_df = agg_df.replace([np.nan], [None])
        return px.pie(agg_df, names=names_col, values=agg_col_name)

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
        elif build_from == 'agg':
            fig = self.using_agg(evaluator=self.evaluator, **base)

        self._figure = fig
        self._update_layout()
        return self.figure


class PlotlyBar(ReportFigure, PlotlyMixin):
    """
    Столбчатая диаграмма с использованием plotly.
    """
    _orientation = 'v'

    @property
    def orientation(self):
        return self.__class__._orientation

    @property
    def is_vertical(self):
        return self.orientation == 'v'

    def using_agg(self, dataframe=None, groupby=[],
        on='', func='count', legend=[], evaluator=None, **kwargs):
        df = evaluator.get_or_build_dataframe(dataframe)
        kw = {'orientation': self.orientation}

        if groupby:
            if legend:
                return self._using_legend(df, legend, groupby, on, func)

            df = df.groupby(groupby).agg({on: func})
        else:
            df = self._no_groupby(df, on, func)
            x, y = ('index', func) if self.is_vertical else (func, 'index')
            return px.bar(df, x=x, y=y, **kw)

        df, indices_col = self._append_indices(df, groupby)
        agg_col_name = f'{func}({on})'
        df[agg_col_name] = df[on]

        x, y = indices_col, agg_col_name
        if self.orientation == 'h':
             x, y = y, x
        df = df.replace([np.nan], [None])
        return px.bar(df, x=x, y=y, **kw)

    def build(self):
        base, build_from = self.base, self.build_from
        orientation = self.orientation
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
        elif build_from == 'agg':
            fig = self.using_agg(evaluator=self.evaluator, **base)

        self._figure = fig
        fig.update_layout(barmode=self._barmode)
        self._update_layout()
        return self.figure

    def _append_indices(self, df, groupby):
        indices = list(df.index)
        if len(groupby) > 1:
            try:
                indices = [', '.join(i) for i in indices]
            except TypeError:
                _ = []
                for ind in indices:
                    _.append(', '.join([str(i) for i in ind]))
                indices = _
        df = df.reset_index()
        indices_col = ', '.join(groupby)
        df[indices_col] = indices
        return df, indices_col

    def _using_legend(self, df, legend, groupby, on, func):
        groupby_col = ', '.join(groupby)
        for n, l in enumerate(groupby):
            if n == 0:
                df[groupby_col] = df[l].astype('str')
                continue
            df[groupby_col] += ', ' + df[l].astype('str')

        legend_col_name = ', '.join(legend)
        for n, l in enumerate(legend):
            if n == 0:
                df[legend_col_name] = df[l].astype('str')
                continue
            df[legend_col_name] += ', ' + df[l].astype('str')

        distinct_groups = []
        _ = df.drop_duplicates(subset=groupby)[groupby]
        for r in _.to_dict(orient='records'):
            dg = ''
            for n, g in enumerate(groupby):
                if n == 0:
                    dg = r[g]
                    continue
                dg += f', {r[g]}'
            distinct_groups.append(dg)

        distinct_legends = []
        _ = df.drop_duplicates(subset=legend)[legend]
        for r in _.to_dict(orient='records'):
            dl = ''
            for n, l in enumerate(legend):
                if n == 0:
                    dl = r[l]
                    continue
                dl += f', {r[l]}'
            distinct_legends.append(dl)

        values = []
        legend_labels = []
        groups_labels = []
        for dg in distinct_groups:
            for dl in distinct_legends:
                q = f"`{groupby_col}` == '{dg}' & `{legend_col_name}` == '{dl}'"
                _ = df.query(q)
                groups_labels.append(dg)
                values.append(_.agg({on: func})[0])
                legend_labels.append(dl)

        func_col = f'{func}({on})'
        df_dict = {
            groupby_col: groups_labels,
            func_col: values,
            legend_col_name: legend_labels,
        }
        df = pd.DataFrame(df_dict)
        x, y = (groupby_col, func_col) if self.is_vertical else (func_col, groupby_col)
        df = df.replace([np.nan], [None])
        return px.bar(df, x=x, y=y, color=legend_col_name, orientation=self.orientation)


class PlotlyHbar(PlotlyBar, PlotlyMixin):
    _orientation = 'h'


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
