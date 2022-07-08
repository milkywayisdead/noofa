from pandas import concat, DataFrame


class Panda:
    def __init__(self, data):
        self._df = DataFrame(data)

    @property
    def df(self):
        return self._df

    @classmethod
    def is_panda(cls, obj):
        return type(obj) is cls

    @property
    def columns(self):
        return list(self._df.columns)

    def join(self, panda, **kwargs):
        """
        Соединение с другой Panda.
        """
        how = kwargs.get('how', 'inner')
        on = kwargs.get('on', [])

        self._df = self.df.join(panda, how=how, on=on)

        return self

    def union(self, panda, **kwargs):
        """
        Объединение с другой Panda.
        """
        self._df = concat(
            [self.df, panda.df],
        )
        return self

    def where(self, filter_):
        """
        Отсеивание лишних строк.
        """
        self._df = self.df[filter_]
        return self

    def order_by(self, by, **kwargs):
        """
        Упорядочивание строк.
        """
        asc = kwargs.get('asc', True)
        if asc not in [True, False]:
            asc = True

        self._df = self.df.sort_values(by=by, ascending=asc)
        return self

    def group_by(self):
        """
        Группировка строк.
        """
        return self


class PandaFilter:
    pass