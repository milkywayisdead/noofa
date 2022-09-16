"""
Для работы с датафреймами.
"""
import pandas as pd

from . import filters


def new(data={}):
    return pd.DataFrame(data)


def join(df1, df2, on, how='inner'):
    """
    Соединение датафреймов.
    """
    result_df = pd.merge(
        df1, df2, 
        left_on=on[0], right_on=on[1],
        how=how,
    )
    return result_df


def union(dataframes_list):
    """
    Склеивание датафреймов из списка.
    dataframes_list - список датафреймов pandas.
    """
    result = pd.DataFrame()
    for df in dataframes_list:
        result = pd.concat([result, df], ignore_index=True)
    return result


def empty():
    """
    Пустой датафрейм.
    """
    return pd.DataFrame()


def add_column(df, col_name, col_data):
    """
    Добавление столбца к датафрейму.
    """
    df[col_name] = col_data
    return df


def rename_columns(df, aliases_dict, inplace=True):
    """
    Переименование столбца датафрейма.
    df - датафрейм pandas,
    aliases_dict - словарь вида {название_поля:новое название}.
    """
    df.rename(columns=aliases_dict, inplace=inplace)
    return df


def drop_columns(df, cols_list, inplace=True):
    """
    Удаление столбцов.
    """
    for col in cols_list:
        df.drop(col, inplace=inplace, axis=1)
    return df


def filter(df, panda_jsfilters):
    """
    Фильтрация строк датафрейма.
    """
    panda_filter = filters._parse_filters(df, panda_jsfilters)
    return df[panda_filter.filter]


def order_by(df, by, **kwargs):
    """
    Упорядочивание строк датафрейма.
    """
    asc = kwargs.get('asc', True)
    if asc not in [True, False]:
        asc = True
    return df.sort_values(by=by, ascending=asc)


def get_filter(filter_type):
    return filters.PANDA_FILTERS[filter_type]


def lazy_filter(df, pf):
    if isinstance(pf, filters.PandaQ):
        return df[pf.filter]
    return df[pf]