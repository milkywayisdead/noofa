from reports.dataset.base import Panda
from .base import DataframeFunc, NonMandatoryArg, MandatoryArg


class GetDf(DataframeFunc):
    """
    Функция получения датафрейма.
    """
    description = 'Получение датафрейма'
    args_description = [
        MandatoryArg('Название датафрейма', 0),
    ]

    @property
    def name(self):
        return 'get_df'

    def _operation(self, df_name):
        return self.context[df_name]


class GetCol(DataframeFunc):
    """
    Функция получения столбца датафрейма.
    """
    description = 'Получение столбца датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Название столбца', 1),
    ]

    @property
    def name(self):
        return 'get_col'

    def _operation(self, df, col_name):
        return df[col_name]


class GetRow(DataframeFunc):
    """
    Функция получения строки датафрейма.
    """
    description = 'Получение строки датафрейма'
    args_description = [
        MandatoryArg('Датафрейм', 0),
        MandatoryArg('Номер строки', 1),
    ]

    @property
    def name(self):
        return 'get_row'

    def _operation(self, df, index):
        return df.iloc[index]


class Calculator:
    """
    Инструмент для выполнения функций и вычислений. 
    """

    def __init__(self, **kwargs):
        self._dataframes = kwargs.get('dataframes', {})

    def get_df(self, df_name):
        getdf = GetDf(df_name)
        getdf.context = self._dataframes
        return getdf()

    def get_col(self, df, col_name):
        return GetCol(df, col_name)()

    def get_row(self, df, index):
        return GetRow(df, index)()

    def df_merge(self):
        pass

    def df_union(self, df1, df2):
        pass

    def df_query(self, df, q):
        pass