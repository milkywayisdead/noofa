from reports.dataset.base import Panda
from .base import DataframeFunc, NonMandatoryArg, MandatoryArg
from .parser import parse
from ._functions import FUNCTIONS_DICT as _functions_dict
from ._functions import OPERATORS_DICT as _operators_dict
from .errors import FormulaSyntaxError


_OPERATORS_PRIORITY = {
    '*': 1,
    '/': 1,
    '+': 2,
    '-': 2,
}

_OPERATORS = _OPERATORS_PRIORITY.keys()


class Interpreter:
    """
    Инструмент для выполнения функций и вычислений. 
    """

    def __init__(self, **context):
        self._dataframes = context.get('dataframes', {})
        self._variables = context.get('variables', {})
        self._functions_dict = {**_functions_dict}
        self._operators_dict = _operators_dict

    def evaluate(self, expression):
        """
        Получение результата формулы.
        """
        if not expression.endswith(';'):
            expression += ';'
        stree = parse(expression)
        stree = self._normalize_operators(stree[0])
        return self._eval(stree)

    def _eval(self, stree):
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
            left, right = self._eval(stree['left']), self._eval(stree['right'])
            func = self._get_operator(stree['value'])
            return func(left, right)()
        if type_ == 'call':
            args = []
            for arg in stree['args']:
                r = self._eval(arg)
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

    def _get_operator(self, sign):
        return self._operators_dict.get(sign, None)
        
    def _normalize_operators(self, expr):
        """
        Упорядочивание операторов синтаксическом дереве по приоритету операций.
        """
        type_ = expr['type']
        if type_ == 'operator': 
            _unpacked = self._unpack_operator(expr)
            same_priority = self._same_priority(_unpacked)
            # если в распакованном выражении нет операторов с разными
            # приоритетами, то они будут выполняться в порядке появления;
            # в противном случае выполняется их упорядочивание по приоритету
            if not same_priority:
                expr = self._sort_operators(_unpacked)
        elif type_ == 'call':
            args = []
            for arg in expr['args']:
                args.append(self._normalize_operators(arg))
            expr['args'] = args
        return expr

    def _sort_operators(self, unpacked_operator):
        """
        Сортировка операторов по приоритету операций.
        """
        def upd(unp, n, operator):
            left, right = unp[n-1], unp[n+1]
            op = {'type': 'operator', 'value': operator, 'left': left, 'right': right}
            l, r = unp[:n-1], unp[n+2:]
            l.append(op)
            return op, l + r       

        res = []
        # перебор распакованного оператора производится до тех пор,
        # пока он не будет приведён к одному словарю
        while len(unpacked_operator) != 1:
            for n, i in enumerate(unpacked_operator):
                type_ = type(i)
                if type_ is str:
                    priority = _OPERATORS_PRIORITY[i]
                    if priority == 1:
                        # первыми в результат добавляются операторы с приоритетом 1 (*, /)
                        res, unpacked_operator = upd(unpacked_operator, n, i)
                        break
                    else:
                        # для операторов с приоритетом 2 сначала проверяется,
                        # есть ли в распакованном операторе операторы с приоритетом 1 (*, /)
                        keep_looking = ('*' in unpacked_operator) | ('/' in unpacked_operator)
                        if not keep_looking:
                            # если остались только операторы с приоритетом 2, то они последовательно
                            # включаются в результат
                            res, unpacked_operator = upd(unpacked_operator, n, i)
                            break
        return res

    def _unpack_operator(self, op):
        """
        Распаковка аргументов оператора.
        Используется для дальнейшего расположения
        арифмет. операторов в порядке приоритета операций.

        На выходе имеем список вида [токен1, оператор1, ..., операторN-1, токенN]
        """
        res = [op['value']]
        for i in ('left', 'right'):
            o = op[i]
            if o is None and i == 'left':
                continue
            if o['type'] == 'operator':
                unp = self._unpack_operator(o)
                if i == 'left':
                    for i in unp[::-1]:
                        res.insert(0, i)
                else:
                    for i in unp:
                        res.append(i)
            else:
                if i == 'left':
                    res.insert(0, o)
                else:
                    res.append(o)
        return res

    def _same_priority(self, unpacked_operator):
        """
        Проверка распакованного оператора на наличие
        операций с различными приоритетами.
        Возвращает True, если операторы обладают одинаковым
        приоритетом, либо если unpacked_operator пуст.
        """
        same_priority = True
        operators = []
        for i in unpacked_operator:
            type_ = type(i)
            if type_ is str:
                if i in _OPERATORS:
                    operators.append(_OPERATORS_PRIORITY[i])
        if operators:
            operators = set(operators)
            same_priority = len(operators) == 1
        return same_priority

    """
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
    """


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