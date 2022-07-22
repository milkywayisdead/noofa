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
            if self._filter is None:
                self._filter = f
            else:
                self._filter = (self._filter) & f

    def __and__(self, panda_q):
        """
        Логическое умножение с другим составным фильтром.
        """
        if type(panda_q) is PandaQ:
            f = panda_q.filter
            self_f = self.filter
            if f is not None:
                if self_f is not None: 
                    return PandaQ(self.filter, f)
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
                    return PandaQ(self.filter | f)
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


# пример описания фильтра для датафрейма в json
jsfilter = [
    {
        'col_name': 'film.film_id',
        'op': 'lt',
        'value': 35,
        'is_q': False,
    },
    {
        'is_q': True,
        'op': 'or',
        'filters': [
            {
                'col_name': 'film.film_id',
                'op': 'in',
                'value': [33, 35],
                'is_q': False,
            },
            {
                'col_name': 'film.film_id',
                'op': 'eq',
                'value': 22,
                'is_q': False,
            },
        ],
    },
]

_FILTERS = {
    'gt': PandaGt,
    'gte': PandaGte,
    'lt': PandaLt,
    'lte': PandaLte,
    'eq': PandaEq,
    'neq': PandaNeq,
    'contains': PandaContains,
    'startswith': PandaStartsWith,
    'endswith': PandaEndsWith,
    'in': PandaIn,
}