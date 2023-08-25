import math
from pandas import isna

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


def pivot_chart(df, chart_type='line', chart_params={}, **kwargs):
    if chart_type == 'line':
        return _line(df, **chart_params)
    if chart_type == 'pie':
        return _pie(df, **chart_params)
    if chart_type == 'bar':
        return _bar(df, **chart_params)
    if chart_type == 'scatter':
        return _scatter(df, **chart_params)


def _line(df, groupby=[], values=[], x='', y='', misc={}, **kwargs):
    vtp = {
        'method_kw': {
            'mode': 'lines' if not misc.get('markers', False) else 'lines+markers',
            'line_shape': 'linear' if misc.get('line_shape', 'linear') == 'linear' else 'spline',
        },
        'method': go.Scatter,
    }

    return _cartesian_plot(
        df, groupby=groupby, values=values,
        x=x, y=y, method=px.line,
        value_trace_params=vtp,
        plot_params=misc,
    )


def _bar(df, groupby=[], values=[],
    x='', y='', misc={}, **kwargs):

    vtp = {
        'method_kw': {
            'orientation': misc.get('orientation', 'v'),
            'textposition': 'auto',
            'bar_text': misc.get('text_auto', False),
            'text': '',
        },
        'method': go.Bar,
    }

    return _cartesian_plot(
        df, groupby=groupby, values=values,
        x=x, y=y, method=px.bar,
        value_trace_params=vtp,
        plot_params=misc,
    )


def _scatter(df, groupby=[], values=[],
    x='', y='', misc={}, **kwargs):

    vtp = {
        'method_kw': {
            'orientation': misc.get('orientation', 'v'),
            'mode': 'markers',
        },
        'method': go.Scatter,
    }

    return _cartesian_plot(
        df, groupby=groupby, values=values,
        x=x, y=y, method=px.scatter,
        value_trace_params=vtp,
        plot_params=misc,
    )


def _pie(df, groupby=[], values=[],
    x='', y='', misc={}, **kwargs):
    pie = px.pie
    exc = ('', '--')
    not_xy = x in exc or y in exc

    # если нет группировки
    if not groupby:
        if not_xy:
            return pie()
        return pie(df, values=y, names=x, **misc)

    # количество диаграмм равно количеству значений
    groups, subplots = len(groupby), len(values)

    # если есть группировка и 1 значение
    if groups and subplots == 1:
        value = values[0]
        df, indices_col, agg_col_name = _slice(df, groupby, value)
        return pie(df, names=indices_col, values=agg_col_name, **misc)

    # если есть группировка и значений несколько
    if groups and subplots > 1:
        sq = math.sqrt(subplots)
        n = math.ceil(sq)
        cols_n = n
        rows_n = math.ceil(subplots/n)
        spec = {"type": "domain"}
        specs = []
        i = 0
        s = []
        while i != cols_n*rows_n:
            s.append(spec)
            if len(s) == cols_n:
                specs.append(s)
                s = []
            i += 1
        st = [f'{v["func"]}({v["column"]})' for v in values]
        fig = make_subplots(
            cols=cols_n, rows=rows_n,
            specs=specs, subplot_titles=st)

        r, c = 1, 1
        for v in values:
            _, indices_col, agg_col_name = _slice(df, groupby, v)
            fig.add_trace(
                go.Pie(
                    name=f'{agg_col_name}',
                    labels=_[indices_col],
                    values=_[agg_col_name],
                    hovertemplate='%s=%%{label}<br>%s=%%{value}<extra></extra>' % (indices_col, agg_col_name),
                ),
                row=r, col=c
            )
            if c + 1 > cols_n:
                c = 1
                r += 1
            else:
                c += 1

        return fig

    return pie(**misc)


def _slice(df, groupby, value):
    col, func = value['column'], value['func']
    agg_df = df.groupby(groupby).agg({col: func})
    agg_df, indices_col = _append_indices(agg_df, groupby)
    agg_col_name = f'{func}({col})'
    agg_df[agg_col_name] = agg_df[col]
    return agg_df, indices_col, agg_col_name


def _append_indices(df, groupby):
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


def _add_sline(fig, df, value, orientation='v', group=None):
    col, func = value['column'], value['func']
    ser = df.agg({col: func})
    v = float(ser[0])
    ann = f'{func}({col})={v}'
    if group:
        ann += f' ({group})'

    kw = {
        'line_dash': 'dot',
        'annotation_text': ann,
        'annotation_position': 'bottom left',
    }
    if orientation == 'h':
        fig.add_vline(x=v, **kw)
    else:
        fig.add_hline(y=v, **kw)
    return fig


def _add_groupby_col(df, groupby):
    groupby_col = ', '.join(groupby)
    for n, col in enumerate(groupby):
        if n == 0:
            df[groupby_col] = df[col].astype('str')
            continue
        df[groupby_col] += ', ' + df[col].astype('str')
    return df, groupby_col


def _get_value_trace(df, groupby, value, method=go.Scatter,
    orientation='v', method_kw={}, **kwargs):
    col, func = value['column'], value['func']
    x_values, y_values, names = [], [], []
    grouped = df.groupby(groupby)
    for name, group in grouped:
        y_value = group.agg({col: func})
        y_value = float(y_value[0])
        if not isna(y_value):
            x_values.append(name)
            y_values.append(y_value)
    label = f'{func}({col})'

    text = method_kw.setdefault('bar_text', False)
    if text:
        method_kw['text'] = y_values
    if orientation == 'h':
        x_values, y_values = y_values, x_values
        if text:
            method_kw['text'] = x_values
    method_kw.pop('bar_text')
    vl = method(
        name=label,
        x=x_values,
        y=y_values,
        hovertemplate='%s<br>%s=%%{x}<br>%%{y}<extra></extra>' % (label, groupby),
        **method_kw,
    )
    return vl


def _cartesian_plot(df, groupby=[], values=[], x='', y='',
    method=px.line, exc=['', '--'],
    plot_params={}, value_trace_params={}, **kwargs):

    plot = method
    empty = plot()
    not_xy = x in exc or y in exc

    orientation = plot_params.get('orientation', 'v')
    if orientation == 'h':
        x, y = y, x

    # нет группировки
    if not groupby:
        if not_xy:
            return empty

        fig = plot(df, x=x, y=y, **plot_params)
        if not values:
            return fig
        # если есть значения
        for value in values:
            fig = _add_sline(fig, df, value, orientation=orientation)
        return fig

    # если группировать по одному полю
    if len(groupby) == 1:
        groupby_col = groupby[0]
    else:
        df, groupby_col = _add_groupby_col(df, groupby)

    # если нет значений
    if not values:
        if not_xy:
            return empty
        return plot(df, x=x, y=y, color=groupby_col, **plot_params)

    # если не указаны x или y
    if not_xy:
        fig = plot(**plot_params)
        for value in values:
            fig.add_trace(
                _get_value_trace(df, groupby_col, value,
                    orientation=orientation, **value_trace_params)
            )
        return fig

    # если есть x, y, группировка и значения,
    # то для каждой линии достраиваются пунктирные линии значений
    fig = plot(df, x=x, y=y, color=groupby_col, **plot_params)
    grouped = df.groupby(groupby_col)
    for name, group in grouped:
        for value in values:
            fig = _add_sline(fig, group, value,
                group=name, orientation=orientation)
    return fig
