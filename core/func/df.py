from datetime import datetime, date, time

from .base import DataframeFunc, MandatoryArg, NonMandatoryArg
from ..sources.conn import DataQueryResult
from ..dataframes import panda_builder


_DF = panda_builder.pd.DataFrame


class Join(DataframeFunc):
    """
    Функция соединения датафреймов.
    """
    description = 'Функция соединения датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0, [_DF]),
        MandatoryArg('Датафрейм2', 1, [_DF]),
        MandatoryArg('Поле первого датафрейма', 2, [str]),
        MandatoryArg('Поле второго датафрейма', 3, [str]),
        MandatoryArg('Тип объединения', 4, [str]),
    ]

    @classmethod
    def get_name(self):
        return 'df_join'

    def _operation(self, *args):
        df1, df2 = args[0], args[1]
        lo, ro = args[2], args[3]
        join_type = args[4]
        joined = panda_builder.join(df1, df2, [lo, ro], join_type)
        return joined


class Union(DataframeFunc):
    """
    Функция объединения датафреймов.
    """
    description = 'Функция объединения датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0, [_DF]),
        MandatoryArg('Датафрейм2', 1, [_DF]),
    ]

    @classmethod
    def get_name(self):
        return 'df_union'

    def _operation(self, *args):
        return panda_builder.union(list(args))


class Order(DataframeFunc):
    """
    Функция упорядочивания строк датафреймов.
    """
    description = 'Функция упорядочивания строк датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0, [_DF]),
        MandatoryArg('Поле', 1, [str]),
        NonMandatoryArg('Направление', 2, [str]),
    ]

    @classmethod
    def get_name(cls):
        return 'df_order'

    def _operation(self, *args):
        asc = True
        try:
            asc = args[2]
            asc = False if asc == 'desc' else True
        except IndexError:
            pass
        return panda_builder.order_by(args[0], args[1], asc=asc)


class DfFilterDict:
    """
    Обёртка для фильтров датафреймов в виде словарей.
    Используется для простого формирования и сложения фильтров в
    строках выражений.
    """
    def __init__(self, dff_dict):
        self._q = dff_dict

    @property
    def df_filter(self):
        return self._q

    def __and__(self, value):
        return DfFilterDict({
            'is_q': True,
            'op': 'and',
            'filters': [self.df_filter, value.df_filter],
        })

    def __or__(self, value):
        return DfFilterDict({
            'is_q': True,
            'op': 'or',
            'filters': [self.df_filter, value.df_filter],
        })

class DfFilter(DataframeFunc):
    """
    Функция создания фильтров для датафреймов.
    """
    description = 'Функция создания фильтров для датафреймов'
    args_description = [
        MandatoryArg('Название столбца', 1, [str]),
        MandatoryArg('Тип фильтра', 2, [str]),
        MandatoryArg('Значение', 3, [str, int, float, date, time, datetime, bool]),
    ]

    @classmethod
    def get_name(cls):
        return 'df_filter'

    def _operation(self, *args):
        return DfFilterDict({
            'is_q': False,
            'col_name': args[0],
            'op': args[1],
            'value': args[2],
        })


class Filter(DataframeFunc):
    """
    Функция применения фильтров датафреймов.
    """
    description = 'Функция применения фильтров датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0, [_DF]),
        MandatoryArg('Фильтр', 1, [DfFilterDict]),
    ]

    @classmethod
    def get_name(cls):
        return 'filter'

    def _operation(self, *args):
        filters = args[1]
        if not isinstance(filters, list):
            filters = [filters.df_filter]
        else:
            filters = [f.df_filter for f in filters]
        return panda_builder.filter(args[0], filters)


class DfQuery(DataframeFunc):
    """
    Функция выборки данных из датафрейма.
    """
    description = 'Функция выборки данных из датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0, [_DF]),
        MandatoryArg('Строка запроса', 1, [str]),
    ]

    @classmethod
    def get_name(cls):
        return 'df_query'

    def _operation(self, *args):
        return args[0].query(args[1])


class AddColumn(DataframeFunc):
    """
    Функция добавления/изменения столбцов датафреймов.
    """
    description = 'Функция добавления/изменения столбцов датафреймов'
    args_description = [
        MandatoryArg('Датафрейм', 0, [_DF]),
        MandatoryArg('Название столбца', 1, [str]),
        MandatoryArg('Значения', 2),
    ]

    @classmethod
    def get_name(cls):
        return 'add_column'

    def _operation(self, *args):
        df, col_name, values = args[0], args[1], args[2]
        return panda_builder.add_column(df, col_name, values)


class GetColumn(DataframeFunc):
    """
    Функция получения столбца датафрейма.
    """
    description = 'Функция получения столбца датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0, [_DF]),
        MandatoryArg('Название столбца', 1, [str]),
    ]

    @classmethod
    def get_name(cls):
        return 'get_column'

    def _operation(self, *args):
        return args[0][args[1]]


class Head(DataframeFunc):
    """
    Функция получения n первых строк датафрейма.
    """
    description = 'Функция получения n первых строк датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0, [_DF]),
        MandatoryArg('Количество строк', 1, [int]),
    ]

    @classmethod
    def get_name(self):
        return 'df_head'

    def _operation(self, *args):
        return args[0].head(args[1])


class Tail(DataframeFunc):
    """
    Функция получения n последних строк датафрейма.
    """
    description = 'Функция получения n последних строк датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0, [_DF]),
        MandatoryArg('Количество строк', 1, [int]),
    ]

    @classmethod
    def get_name(self):
        return 'df_tail'

    def _operation(self, *args):
        return args[0].tail(args[1])

class DfCount(DataframeFunc):
    """
    Функция получения количества строк датафрейма.
    """
    description = 'Функция получения количества строк датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0, [_DF]),
    ]

    @classmethod
    def get_name(self):
        return 'df_count'

    def _operation(self, *args):
        df = args[0]
        return df.shape[0]


class CreateDataframe(DataframeFunc):
    """
    Функция создания датафрейма.
    """
    description = 'Функция создания датафреймов'
    args_description = [
        NonMandatoryArg('Данные', 0, [_DF, list, DataQueryResult]),
    ]

    @classmethod
    def get_name(cls):
        return 'dataframe'

    def _operation(self, *args):
        if not args:
            return panda_builder.new()
        data = args[0]
        if isinstance(data, DataQueryResult):
            return panda_builder.new(data.data, data.columns)
        if data:
            columns = data.pop(0)
            return panda_builder.new(data, columns)
        return panda_builder.new(data)
