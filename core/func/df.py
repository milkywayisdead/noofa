from .base import DataframeFunc, MandatoryArg, NonMandatoryArg
from ..dataframes import panda_builder


class Build(DataframeFunc):
    """
    Функция создания датафреймов.
    """
    description = 'Функция создания датафреймов'
    args_description = [
        MandatoryArg('Данные', 1),
    ]

    @classmethod
    def get_name(cls):
        return 'df_build'

    def _operation(self, *args):
        return panda_builder.DataFrame(args[0])


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


class DfFilter(DataframeFunc):
    """
    Функция создания фильтров для датафреймов.
    """
    description = 'Функция создания фильтров для датафреймов'
    args_description = [
        MandatoryArg('Датафрейм1', 0),
        MandatoryArg('Тип фильтра', 2),
        MandatoryArg('Название столбца', 1),
        MandatoryArg('Значение', 3),
    ]

    @classmethod
    def get_name(cls):
        return 'df_filter'

    def _operation(self, *args):
        df, filter_type = args[0], args[2]
        col_name, value = args[1], args[3]
        pf = panda_builder.get_filter(filter_type)
        pf = pf(col_name, value)
        pf.df(df)
        return pf


class QDfFilter(DataframeFunc):
    """
    Функция создания составных фильтров для датафреймов.
    """
    description = 'Функция создания составных фильтров для датафреймов'
    args_description = [
        MandatoryArg('Простой фильтр', 0),
    ]

    @classmethod
    def get_name(cls):
        return 'df_cfilter'

    def _operation(self, *args):
        return panda_builder.filters.PandaQ(*args)


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
        return panda_builder.lazy_filter(args[0], args[1])


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


class Head(DataframeFunc):
    """
    Функция получения n первых строк датафрейма.
    """
    description = 'Функция получения n первых строк датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Количество строк', 1),
    ]

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

    def _operation(self, *args):
        return args[0].tail(args[1])


class GroupBy(DataframeFunc):
    pass