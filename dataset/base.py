from pandas import merge, concat, DataFrame


class Panda:
    """
    Датафрейм. Обёртка для датафрейма pandas.
    """
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

    @property
    def shape(self):
        return self._df.shape

    def join(self, panda, **kwargs):
        """
        Соединение с другой Panda.
        """
        how = kwargs.get('how', 'inner')
        on = kwargs.get('on')

        new_df = merge(
            self.df, panda.df, 
            left_on=on[0], right_on=on[1],
            how=how
        )
        self._df = new_df

        return self

    def union(self, panda, **kwargs):
        """
        Объединение с другой Panda.
        """
        ignore_index = kwargs.get('ignore_index', True)

        self._df = concat(
            [self.df, panda.df],
            ignore_index=ignore_index,
        )
        return self

    def add_column(self, col_name, col_data, **kwargs):
        """
        Добавление столбца.
        """
        pass

    def drop_column(self, col_name):
        """
        Удаление столбца.
        """
        self._df.drop(col_name, axis=1, inplace=True)

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

    def apply_func(self, col, func, **kwargs):
        """
        Применение функции к датафрейму.
        """
        return self


def test():
    from reports.tests import pg
    pg.open()
    t1 = pg.get_table('film')
    t2 = pg.get_table('film_actor')
    p1 = Panda(pg.get_data(t1.select()))
    p2 = Panda(pg.get_data(t2.select()))
    pg.close()
    return p1, p2