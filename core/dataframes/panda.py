"""
Для работы с датафреймами.
"""
from pandas import merge, concat, DataFrame


def join(df1, df2, on, how='inner'):
    """
    Соединение датафреймов.
    """
    result_df = merge(
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
    result = DataFrame()
    for df in dataframes_list:
        result = concat([result, df], ignore_index=True)
    return result


def empty():
    pass


def add_column():
    pass


def rename_columns(df, aliases):
    pass


def filter():
    pass


def order_by(df):
    pass
