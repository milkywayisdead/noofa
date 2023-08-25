"""
Интерпретатор функций.
"""
from .parser import parse
from .context import Context, _context_funcs, GetFromContext, GetSlice
from ._functions import FUNCTIONS_DICT as _functions_dict
from ._functions import OPERATORS_DICT as _operators_dict
from .operators import _OPERATORS_PRIORITY
from .errors import ExpressionSyntaxError


_OPERATORS = _OPERATORS_PRIORITY.keys()


class Interpreter:
    """
    Интерпретатор для выполнения функций и вычислений.
    """
    def __init__(self, **context):
        self._functions_dict = {**_functions_dict}
        self._functions_dict.update(_context_funcs)
        self._operators_dict = _operators_dict
        self._context = Context(**context)
        self._connections = {}

    def add_values(self, values_list, evaluator):
        self._context.add_values(values_list, evaluator)

    def get_value(self, name):
        return self._context.get_value(name)

    def update_value(self, name, value):
        self._context.update_value(name, value)

    def evaluate(self, expression):
        """
        Получение результата формулы.
        """
        if not expression.endswith(';'):
            expression += ';'
        stree = parse(expression)
        stree = self._normalize_operators(stree[0])
        is_valid = self._check_syntax(stree)
        if not is_valid:
            raise ExpressionSyntaxError
        func = self._eval(stree)
        result = func()
        return result

    def apply(self, df, expr):
        """
        Применение выражения к строкам датафрейма.
        Здесь исользуется локальный контекст интерпретатора,
        при этом в выражении будут доступны переменные row - строка датафрейма в виде словаря,
        и idx - порядковый номер строки. Нумерация строк - с 0.
        """
        result = []
        rows = df.to_dict(orient='records')
        self._context.switch_to_local()
        key = 'row'
        for idx, row in enumerate(rows):
            self.add_to_local(key, row)
            self.add_to_local('idx', idx)
            result.append(self.evaluate(expr))
        if result:
            self._context.remove(key)
            self._context.remove('idx')
        self._context.switch_to_global()
        return result

    def add_to_global(self, key, value):
        """
        Добавление ключа-значения в глобальный контекст.
        """
        self._context.add_to_global(key, value)

    def add_to_local(self, key, value):
        """
        Добавление ключа-значения в локальный контекст.
        """
        self._context.add_to_local(key, value)

    def _check_syntax(self, stree):
        """
        Проверка синтаксиса выражения/части выражения.
        При наличии ошибки возвращает False.
        """
        if stree is None:
            return True
        type_ = stree['type']
        if type_ == 'symbol':
            return True
        if type_ == 'number':
            if stree['value'].count('.') > 1:
                return False
        if type_ == 'operator':
            sign = stree['value']
            left, right = stree['left'], stree['right']
            for o in (left, right):
                if not self._check_syntax(o):
                    return False
            if left is None:
                if not sign in ('+', '-'):
                    return False
            if right is None:
                return False
        if type_ == 'context':
            args = stree['args']
            for arg in args:
                if not self._check_syntax(arg):
                    return False
            var_ = stree['var']
            if var_ is None:
                return False
            if len(args) == 0:
                return False
        if type_ == 'call':
            args = stree['args']
            for arg in args:
                if not self._check_syntax(arg):
                    return False
            fname = stree['function']
            args_len = len(args)
            if fname is None:
                if not args_len or args_len > 1:
                    return False
        return True

    def _eval(self, stree):
        """
        Интерпретация синтаксического дерева с возвращением результата.
        """
        if stree is None:
            return None
        type_ = stree['type']
        if type_ == 'symbol':
            _func = self._get_function(GetFromContext.get_name())
            return _func(self._context, stree['value'])
        if type_ == 'string':
            func = self._get_function('to_str')
            return func(stree['value'])
        if type_ == 'number':
            value = stree['value']
            if '.' in value:
                _func = 'to_float'
            else:
                _func = 'to_int'
            func = self._get_function(_func)
            return func(value)
        if type_ == 'operator':
            sign = stree['value']
            left, right = self._eval(stree['left']), self._eval(stree['right'])
            func = self._get_operator(sign)
            return func(left, right)
        if type_ == 'context':
            slice_ = []
            for arg in stree['args']:
                r = self._eval(arg)
                slice_.append(r())
            var_ = stree['var']['value']
            _func = self._get_function(GetSlice.get_name())
            var_ = self._context.get(var_)
            return _func(var_, slice_)
        if type_ == 'call':
            args = []
            for arg in stree['args']:
                r = self._eval(arg)
                args.append(r)
            _func = stree['function']
            if _func is None:
                return args[0]
            else:
                fname = _func['value']
                func = self._get_function(fname)
                if func.group == 'context':
                    args.insert(0, self._context)
                #if _func['value'] == 'connection':
                #    return func(self._connections, *args)
            return func(*args)

    def _get_function(self, name):
        return self._functions_dict.get(name, None)

    def _get_operator(self, sign):
        return self._operators_dict.get(sign, None)

    def _normalize_operators(self, expr):
        """
        Упорядочивание операторов в выражении по приоритету операций.
        """
        type_ = expr['type']
        if type_ == 'operator':
            _unpacked = self._unpack_operator(expr)
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

        def get_prioritized(priority):
            return [s for s, p in _OPERATORS_PRIORITY.items() if p == priority]

        res = []
        current_priority = 1
        prioritized_operators = get_prioritized(current_priority)
        # перебор распакованного оператора производится до тех пор,
        # пока он не будет приведён к одному словарю
        while len(unpacked_operator) != 1:
            for n, i in enumerate(unpacked_operator):
                type_ = type(i)
                if type_ is str:
                    priority = _OPERATORS_PRIORITY[i]
                    if priority == current_priority:
                        res, unpacked_operator = upd(unpacked_operator, n, i)
                        break
                    else:
                        keep_looking = False
                        for p in prioritized_operators:
                            if p in unpacked_operator:
                                keep_looking = True
                                break
                        if not keep_looking:
                            #res, unpacked_operator = upd(unpacked_operator, n, i)
                            current_priority += 1
                            prioritized_operators = get_prioritized(current_priority)
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
            if o is None:
                if i == 'left':
                    res.insert(0, o)
                else:
                    res.append(o)
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
