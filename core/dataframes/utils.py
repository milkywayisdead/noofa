from . import panda_builder


_ISNAN = panda_builder.pd.isna


def get_df_descriptor(df, ignore_nan_as_unique=False):
    """
    Получить описыватель датафрейма.
    """
    return DfDescriptor(df, ignore_nan_as_unique=ignore_nan_as_unique)


class DfDescriptor:
    """
    Описыватель датафрейма. Содержит список столбцов,
    уникальных значений и типов данных.

    ignore_nan_as_unique - учитывать ли значения nan при получении
    списка уникальных значений по столбцам. Не учитывать при True.
    """
    def __init__(self, df, ignore_nan_as_unique=False):
        self.columns = sorted(list(df.columns))
        self.dtypes = get_dtypes(df)
        self.unique = get_unique(df, ignore_nan_as_unique=ignore_nan_as_unique)

    def describe(self):
        return {
            'columns': self.columns,
            'dtypes': self.dtypes,
            'unique': self.unique,
        }


def get_dtypes(df):
    """
    Получение словаря с типами данных в столбцах дф.
    """
    _ = df.dtypes.to_dict()
    dtypes = {col: str(dtype) for col, dtype in _.items()}
    return dtypes


def get_unique(df, cols=None, ignore_nan_as_unique=False):
    """
    Получение уникальных значений по столбцу
    (при cols is None - по всем столбцам) датафрейма.
    """
    unique_values = {}
    if cols is None:
        cols = list(df.columns)
    for col in cols:
        u = df[col].unique()
        if ignore_nan_as_unique == True:
            u = [i for i in u if not _ISNAN(i)]
        else:
            u = list(u)

        try:
            u.sort()
        except:
            pass
        unique_values[col] = u

    return unique_values


def new_df(data, columns):
    return panda_builder.new(data, columns)
