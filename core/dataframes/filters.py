"""
Фильтры для датафреймов.
"""

from abc import ABC, abstractmethod


class PandaFilter(ABC):
    """
    Простой фильтр для датафреймов.
    """
    def __init__(self, panda_col, value):
        self._panda_col = panda_col  # название столбца
        self._value = value  # значение, с которым сравнивается значение в ячейке
        self._df = None

    def __and__(self, panda_filter):
        return self.filter & panda_filter.filter

    def __or__(self, panda_filter):
        return self.filter | panda_filter.filter

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    @abstractmethod
    def filter(self):
        pass


class PandaQ:
    """
    Составной фильтр для датафреймов.
    """
    def __init__(self, *panda_filters):
        self._filter = None
        for f in panda_filters:
            if self.is_empty:
                self._filter = f.filter
            else:
                self._filter = (self._filter) & f.filter

    @property
    def is_empty(self):
        return self._filter is None

    def __and__(self, panda_q):
        """
        Логическое умножение с другим составным фильтром.
        """
        if type(panda_q) is PandaQ:
            f = panda_q.filter
            self_f = self.filter
            if f is not None:
                if self_f is not None: 
                    self._filter = self.filter & f
                    return self
                else:
                    return panda_q
        return self

    def __or__(self, panda_q):
        """
        Логическое сложение с другим составным фильтром.
        """
        if type(panda_q) is PandaQ:
            f = panda_q.filter
            self_f = self.filter
            if f is not None:
                if self_f is not None:
                    self._filter = self.filter | f
                    return self
                else:
                    return panda_q
        return self

    @property
    def filter(self):
        return self._filter


class PandaEq(PandaFilter):
    """
    Простой фильтр равенства.
    """
    @property
    def filter(self):
        return self._df[self._panda_col] == self._value


class PandaNeq(PandaFilter):
    """
    Простой фильтр неравенства.
    """
    @property
    def filter(self):
        return self._df[self._panda_col] != self._value


class PandaGte(PandaFilter):
    """
    Простой фильтр 'больше либо равно'.
    """
    @property
    def filter(self):
        return self._df[self._panda_col] >= self._value


class PandaGt(PandaFilter):
    """
    Простой фильтр 'больше, чем'.
    """
    @property
    def filter(self):
        return self._df[self._panda_col] > self._value


class PandaLte(PandaFilter):
    """
    Простой фильтр 'меньше либо равно'.
    """
    @property
    def filter(self):
        return self._df[self._panda_col] <= self._value


class PandaLt(PandaFilter):
    """
    Простой фильтр 'меньше, чем'.
    """
    @property
    def filter(self):
        return self._df[self._panda_col] < self._value


class PandaContains(PandaFilter):
    """
    Простой фильтр проверки наличия значения.
    """
    @property
    def filter(self):
        return self._df[self._panda_col].str.contains(self._value)


class PandaStartsWith(PandaFilter):
    """
    Простой фильтр проверки того, начинается ли строка с подстроки.
    """
    @property
    def filter(self):
        return self._df[self._panda_col].str.lower().str.startswith(self._value)


class PandaEndsWith(PandaFilter):
    """
    Простой фильтр проверки того, заканчивается ли строка подстрокой.
    """
    @property
    def filter(self):
        return self._df[self._panda_col].str.lower().str.endswith(self._value)


class PandaIn(PandaFilter):
    """
    Простой фильтр проверки включенности элемента в список.
    """
    @property
    def filter(self):
        return self._df[self._panda_col].isin(self._value)


PANDA_FILTERS = {
    '>': PandaGt,
    '>=': PandaGte,
    '<': PandaLt,
    '<=': PandaLte,
    '==': PandaEq,
    '!=': PandaNeq,
    'contains': PandaContains,
    'startswith': PandaStartsWith,
    'endswith': PandaEndsWith,
    'in': PandaIn,
}


def _parse_filter(df, panda_jsf):
    if panda_jsf['is_q'] == True:
        filters = []
        for f in panda_jsf['filters']:
            filters.append(_parse_filter(df, f))
        op = panda_jsf['op']
        if op == 'or':
            panda_filter = PandaQ()
            for f in filters:
                panda_filter |= f
        else:
            panda_filter = PandaQ()
            for f in filters:
                panda_filter &= f
        return panda_filter
    else:
        col, op, value = panda_jsf['col_name'], panda_jsf['op'], panda_jsf['value']
        panda_filter = PANDA_FILTERS[op](col, value)
        panda_filter.df = df
        return PandaQ(panda_filter)

def _parse_filters(df, panda_jsfilters):
    """
    Построение фильтра из json.
    """
    res = PandaQ()
    for f in panda_jsfilters:
        p = _parse_filter(df, f)
        res &= p
    return res