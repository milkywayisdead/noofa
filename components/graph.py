"""
Для построения графиков и прочего.
"""

from abc import ABC, abstractmethod
import plotly.express as px
import plotly.graph_objects as go


class Fig(ABC):
    def __init__(self, **options):
        pass

    @abstractmethod
    def add_values(self, **options):
        pass

    @abstractmethod
    def _get_base(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def build(self, **options):
        pass


class PlotlyLine(Fig):
    def add_values(self, **options):
        pass

    def _get_base(self):
        return px.line

    def to_dict(self):
        pass

    def build(self, **options):
        pass


class PloltyPie(Fig):
    def add_values(self, **options):
        pass

    def _get_base(self):
        return px.pie

    def to_dict(self):
        pass

    def build(self, **options):
        pass


class PloltyBar(Fig):
    orientation = 'v'
    def add_values(self, **options):
        pass

    def _get_base(self):
        return px.bar

    def to_dict(self):
        pass

    def build(self, **options):
        pass


class PlotlyHbar(PloltyBar):
    orientation = 'h'
    pass


FIGURES = {
    'plotly': {
        'line': PlotlyLine,
        'bar': PloltyBar,
        'pie': PloltyBar,
        'hbar': PlotlyHbar,
    },
}