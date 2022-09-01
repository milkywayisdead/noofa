from pandas import merge, concat, DataFrame

from .filters import PandaQ, _FILTERS


class Panda:
    """
    Датафрейм. Обёртка для датафрейма pandas.
    """
    def __init__(self, data):
        self._df = DataFrame(data)

    @property
    def df(self):
        return self._df

    def __repr__(self):
        return repr(self.df)

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
        self.df[col_name] = col_data
        return self

    def rename_columns(self, rm_dict={}):
        """
        Переименование столбцов.
        """
        self._df.rename(columns=rm_dict, inplace=True)
        return self

    def drop_columns(self, col_name):
        """
        Удаление столбца.
        """
        self._df.drop(col_name, axis=1, inplace=True)
        return self

    def modify_column_type(self, col_name, to_type='str'):
        """
        Изменение типа данных в столбце.
        """
        t = str
        if to_type == 'int':
            t = int
        elif to_type == 'float':
            t = float
        self.df[col_name] = self.df[col_name].astype(t) 
        return self

    def filter(self, panda_filter):
        """
        Фильтрация строк.
        """
        self._df = self.df[panda_filter.filter]
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

    def _parse_filter(self, jsf):
        if jsf['is_q'] == True:
            filters = []
            for f in jsf['filters']:
                filters.append(self._parse_filter(f))
            op = jsf['op']
            if op == 'or':
                panda_filter = PandaQ()
                for f in filters:
                    panda_filter |= PandaQ(f)
            else:
                panda_filter = PandaQ(*filters)
            return panda_filter
        else:
            col, op, value = jsf['col_name'], jsf['op'], jsf['value']
            panda_filter = _FILTERS[op](col, value)
            panda_filter.df(self.df)
            return panda_filter

    def parse_filters(self, jsfilters):
        """
        Построение фильтра из json.
        """
        filters = []
        for f in jsfilters:
            filters.append(self._parse_filter(f))
        return PandaQ(*filters)