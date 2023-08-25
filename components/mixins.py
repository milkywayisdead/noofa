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
        return {
            'data': self.figure.to_dict(),
            'title': self.title_text,
            'id': self.id,
        }

    def to_png(self, path):
        if not path.endswith('.png'):
            path += '.png'
        self.figure.write_image(path)

    def _no_groupby(self, dataframe, on, func):
        ser = dataframe.agg({on: func})
        df = ser.to_frame(name=func)
        df = df.reset_index()
        return df
