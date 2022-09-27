from .base import DataframeFunc, MandatoryArg, NonMandatoryArg
from ..dataframes import panda_builder


class Join(DataframeFunc):
    """
    Функция соединения датафреймов.
    """
    description = 'Функция соединения датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0),
        MandatoryArg('Датафрейм2', 1),
        MandatoryArg('Поле первого датафрейма', 2),
        MandatoryArg('Поле второго датафрейма', 3),
        MandatoryArg('Тип объединения', 4),
    ]

    @classmethod
    def get_name(self):
        return 'df_join'

    def _operation(self, *args):
        df1, df2 = args[0], args[1]
        on = [args[2], args[3]]
        join_type = args[4]
        joined = panda_builder.join(df1, df2, on, join_type)
        return joined


class Union(DataframeFunc):
    """
    Функция объединения датафреймов.
    """
    description = 'Функция объединения датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0),
        MandatoryArg('Датафрейм2', 1),
    ]

    @classmethod
    def get_name(self):
        return 'df_union'

    def _operation(self, *args):
        return panda_builder.union(args)


class Order(DataframeFunc):
    """
    Функция упорядочивания строк датафреймов.
    """
    description = 'Функция упорядочивания строк датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0),
        MandatoryArg('Поле', 1),
        NonMandatoryArg('Направление', 2),
    ]

    @classmethod
    def get_name(cls):
        return 'df_order'

    def _operation(self, *args):
        asc = True
        try:
            asc = args[2]
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
        MandatoryArg('Название столбца', 1),
        MandatoryArg('Тип фильтра', 2),
        MandatoryArg('Значение', 3),
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
        MandatoryArg('Датафрейм1', 0),
        MandatoryArg('Фильтр', 1),
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
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Строка запроса', 1),
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
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Название столбца', 1),
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
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Название столбца', 1),
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
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Количество строк', 1),
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
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Количество строк', 1),
    ]

    @classmethod
    def get_name(self):
        return 'df_tail'

    def _operation(self, *args):
        return args[0].tail(args[1])


class CreateDataframe(DataframeFunc):
    """
    Функция создания датафрейма.
    """
    description = 'Функция создания датафреймов'
    args_description = [
        NonMandatoryArg('Данные', 0),
    ]

    @classmethod
    def get_name(cls):
        return 'dataframe'

    def _operation(self, *args):
        if not args:
            return panda_builder.new()
        return panda_builder.new(args[0])