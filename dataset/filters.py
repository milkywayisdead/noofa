"""
Фильтры для датафреймов.
"""


class PandaFilter:
    """
    Фильтр строк для датафреймов.
    """
    def __init__(self, panda_col, value):
        self._panda_col = panda_col
        self._value = value

    def __and__(self, panda_filter):
        pass

    def __or__(self, panda_filter):
        pass

    def make(self):
        pass


class PandaQ:
    def __init__(self, panda_filter1, panda_filter2):
        self._filter = panda_filter1 & panda_filter2

    def __and__(self, panda_filter):
        pass

    def __or__(self, panda_filter):
        pass


class PandaEq(PandaFilter):
    def make(self):
        return self._panda_col == self._value


class PandaNeq(PandaFilter):
    def make(self):
        return self._panda_col != self._value


class PandaGte(PandaFilter):
    def make(self):
        return self._panda_col >= self._value


class PandaGt(PandaFilter):
    def make(self):
        return self._panda_col > self._value


class PandaLte(PandaFilter):
    def make(self):
        return self._panda_col <= self._value


class PandaLt(PandaFilter):
    def make(self):
        return self._panda_col < self._value


class PandaContains(PandaFilter):
    def make(self):
        return self._panda_col.str.contains(self._values)


class PandaStartsWith(PandaFilter):
    def make(self):
        return self._panda_col.str.lower().str.startswith(self._value)


class PandaEndsWith(PandaFilter):
    def make(self):
        return self._panda_col.str.lower().str.endswith(self._value)


class PandaIn(PandaFilter):
    def make(self):
        return self._panda_col.isin(self._values)