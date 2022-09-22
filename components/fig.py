"""
Для построения графиков и прочего.
"""
from abc import ABC, abstractmethod
import plotly.express as px
import plotly.graph_objects as go

from ..core.dataframes.panda_builder import pd


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
        cols = pd.columns
        if len(cols) == 1:
            return data[cols[0]].to_list()
    return []


def plotly_line(**options):
    """
    Построение line-графиков с использованием plotly.
    """
    data = options['data']
    title = options.get('title', '')
    from_ = options['from']
    if from_ == 'grouped':
        lg = options['line_group']
        fig = px.line(data, title=title,
        x=options['x'], y=options['y'], 
        line_group=lg, color=lg)
    elif from_ == 'line':
        fig = px.line(title=title)
        for d in data:
            x, y, name = d['x'], d['y'], d['name']
            x, y = _to_list(x), _to_list(y)
            fig.add_trace(go.Scatter(x=x, y=y, name=name))
    return fig


def plotly_pie(**options):
    """
    Построение круговой диаграммы с использованием plotly.
    """
    values = options['value']
    title = options['title']
    names = options['names']
    return px.pie(values=values, title=title, names=names)


def plotly_bar(**options):
    """
    Построение столбчатой диаграммы с использованием plotly.
    """
    df = options['df']
    x, y = options['x'], options['y']
    title = options['title']
    labels = options.get('labels', {})
    return px.bar(df, x=x, y=y, title=title, orientation='v', labels=labels)


def plotly_hbar(**options):
    """
    Построение столбчатой диаграммы с горизонтальной ориентацией 
    с использованием plotly.
    """
    df = options['df']
    x, y = options['x'], options['y']
    title = options['title']
    labels = options.get('labels', {})
    return px.bar(df, x=x, y=y, title=title, orientation='h', labels=labels)


_FIG_BUILDERS = {
    'plotly': {
        'line': plotly_line,
        'bar': plotly_bar,
        'pie': plotly_pie,
        'hbar': plotly_hbar,
    },
}


def _get_fig_builder(fig_type, engine='plotly'):
    return _FIG_BUILDERS[engine][fig_type]