"""
Для работы с датафреймами.
"""
from datetime import datetime, date, time
import pandas as pd

from . import filters


def new(data={}, columns=[]):
    return pd.DataFrame(data, columns=columns)


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
    result = dataframes_list.pop(0)
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
    #df[col_name] = col_data
    new_df = df.assign(**{col_name: col_data})
    return new_df


def add_columns(df, columns):
    return df.assign(**columns)


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


def order_by(df, by, asc=True):
    """
    Упорядочивание строк датафрейма.
    """
    return df.sort_values(by=by, ascending=asc)


def get_filter(filter_type):
    return filters.PANDA_FILTERS[filter_type]


def lazy_filter(df, pf):
    if isinstance(pf, filters.PandaQ):
        return df[pf.filter]
    return df[pf]


def astype(df, col=None, dtype=None):
    if dtype == 'datetime':
        dtype = 'datetime64[s]'

    dtype_is_float = dtype == 'float'
    current_types = {c: str(t) for c, t in df.dtypes.to_dict().items()}
    cur_type = current_types[col]
    dt_to_float = cur_type == 'datetime64[ns]' and dtype_is_float
    ns_to_num = cur_type == 'datetime64[ns]' and dtype in ['int', 'float']

    if dt_to_float or ns_to_num:
        df[col] = df[col].astype('int64')
    if ns_to_num:
        df[col] = df[col]/10**9

    return df.astype({col: dtype})


def pivot_table(df, index=None, columns=None, values=None,
    aggfunc='count', fill_value=None, margins=False, **kwargs):
    """
    Сводная таблица.
    """
    if not aggfunc or df.empty:
        return pd.DataFrame()

    agg_func = aggfunc
    if aggfunc and isinstance(aggfunc, dict):
        agg_func = {}
        for col, func in aggfunc.items():
            agg_func[col] = func if isinstance(func, list) and len(func) > 1 else func[0]

    values = list(agg_func.keys()) if margins == True else None
    res = df.pivot_table(index=index, columns=columns, values=values,
        aggfunc=agg_func, fill_value=fill_value, margins=margins)
    return res


def fill_na(df, col='', fill_value=None, **kwargs):
    """
    Заполнение пустых значений.
    """
    assert isinstance(
        fill_value,
        (bool, str, int, float, date, time, datetime),
    ), f'Нельзя использовать значения типа {type(fill_value)}'

    if not col:
        return df.fillna(fill_value) if fill_value is not None else df

    try:
        df[col] = df.loc[:, col].fillna(fill_value)
    except:
        pass
    return df


def drop_na(df, col):
    """
    Отбрасывание строк, в столбцах col которых
    находятся пустые значения.
    """
    try:
        df = df[df[col].notnull()]
    except:
        pass
    return df
