"""
Для построения графиков и прочего.
"""

from abc import ABC, abstractmethod
import plotly.express as px


class PlotlyFig(ABC):
    _base = None
    def __init__(self, **options):
        try:
            options['orientation'] = self.__class__.orientation
        except AttributeError:
            pass
        title = options.get('title', '')
        self._base_figure = self.__class__._base(title=title)
        self._base_figure.update_layout({
            'showlegend': options.get('showlegend', False),
        })

    @property
    def figure(self):
        return self._base_figure

    def get_base_figure(self):
        return self.__class__._base

    @abstractmethod
    def add_dataset(self, **options):
        pass

    def to_dict(self):
        return self.figure.to_dict()
    
    def to_bytes(self):
        return self.figure.to_image()


class PlotlyLine(PlotlyFig):
    _base = px.line
    def add_dataset(self, **options):
        x, y = options.get('x', []), options.get('y', [])
        name = options.get('name', 'line')
        self.figure.add_scatter(x=x, y=y, name=name)


class PloltyPie(PlotlyFig):
    _base = px.pie
    def add_dataset(self, **options):
        values = options.get('x', 0)
        name = options.get('name', 'sector')
        self.figure.add_pie(values=values, name=name)


class PloltyBar(PlotlyFig):
    orientation = 'v'
    _base = px.bar
    def add_dataset(self, **options):
        x, y = options.get('x', []), options.get('y', [])
        name = options.get('name', 'line')
        self.figure.add_bar(x=x, y=y, name=name)


class PlotlyHbar(PloltyBar):
    orientation = 'h'


FIGURES = {
    'plotly': {
        'line': PlotlyLine,
        'bar': PloltyBar,
        'pie': PloltyPie,
        'hbar': PlotlyHbar,
    },
}