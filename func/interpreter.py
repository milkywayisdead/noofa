from reports.dataset.base import Panda
from .base import DataframeFunc, NonMandatoryArg, MandatoryArg
from ._functions import FUNCTIONS_DICT as _functions_dict
from .errors import FormulaSyntaxError


class Interpreter:
    """
    Инструмент для выполнения функций и вычислений. 
    """

    def __init__(self, **context):
        self._dataframes = context.get('dataframes', {})
        self._variables = context.get('variables', {})
        self._functions_dict = {**_functions_dict}

    def eval(self, stree):
        """
        Интерпретация синтаксического дерева с возвращением результата.
        """
        type_ = stree['type']
        if type_ == 'symbol':
            raise FormulaSyntaxError
        if type_ == 'string':
            return str(stree['value'])
        if type_ == 'number':
            return float(stree['value'])
        if type_ == 'operator':
            left, right = self.eval(stree['left']), self.eval(stree['right'])
            func = None
            value = stree['value']
            if value == '+':
                func = 'sum'
            elif value == '-':
                func = 'subtract'
            elif value == '*':
                func = 'mult'
            elif value == '/':
                func = 'div'
            func = self._get_function(func)
            return func(left, right)()
        if type_ == 'call':
            args = []
            for arg in stree['args']:
                r = self.eval(arg)
                args.append(r)
            if stree['function'] is None:
                func = None
            else:
                func = self._get_function(stree['function']['value'])
            if func is None and not args:
                raise FormulaSyntaxError
            return func(*args)()

    def _get_function(self, name):
        """
        Получение функции по имени.
        """
        return self._functions_dict.get(name, None)

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