from pandas import Series

from .base import Func, MandatoryArg, NonMandatoryArg
from .errors import InterpreterContextError


class Context:
    """
    Контекст интерпретатора.
    """
    def __init__(self, **kwargs):
        self.global_context = {**kwargs}  # глобальный контекст (весь отчёт)
        self.local_context = {}  #  локальный контекст (в случае выч. значения в строке или столбце)
        self._current_context = self.global_context
        self._using_local = False

    def switch_to_global(self):
        """
        Переключение контекста на глобальный.
        """
        self._using_local = False
        self._current_context = self.global_context

    def switch_to_local(self):
        """
        Переключение контекста на локальный.
        """
        self._using_local = True
        self._current_context = self.local_context

    def add_to_global(self, key, value):
        """
        Добавление в глобальный контекст.
        """
        self.global_context[key] = value

    def add_to_local(self, key, value):
        """
        Добавление в локальный контекст.
        """
        self.local_context[key] = value

    def add(self, key, value):
        """
        Добавление в текущий контекст.
        """
        self._current_context[key] = value

    def get(self, key):
        """
        Получение значения из текущ. либо глобального контекста.
        """
        try:
            return self._current_context[key]
        except KeyError:
            try:
                return self.global_context[key]
            except KeyError:
                raise InterpreterContextError(key)

    def remove(self, key):
        """
        Удаление из текущего контекста.
        """
        self._current_context.pop(key)


class GetFromContext(Func):
    """
    Функция получения значения из контекста интерпретатора.
    Используется на уровне интерпретатора.
    """
    group = 'context'
    description = 'Функция контекста'
    args_description = [
        MandatoryArg('context', 0),
        MandatoryArg('var', 1),
    ]

    @classmethod
    def get_name(cls):
        return '_getfromcontext'

    def _operation(self, *args):
        return args[0].get(args[1])


class GetSlice(Func):
    """
    Функция получения столбца датафрейма.
    Используется на уровне интерпретатора.
    """
    group = 'context'
    description = 'Функция контекста'
    args_description = [
        MandatoryArg('obj', 0),
        MandatoryArg('col', 1),
    ]

    @classmethod
    def get_name(cls):
        return '_getslice'

    def _operation(self, *args):
        args = list(args)
        obj, key = args.pop(0), args[0]

        # в случае применения функции apply интерпретатора объектом может быть словарь 
        if isinstance(obj, dict):
            result = obj[key[0]]
        else:
            result = obj[key]
            #if len(key) > 1:
            #    result = obj[key]
            #else:
            #    result = obj[[key[0]]]
        #if isinstance(result, Series):
        #    result = result.to_list()
        #if isinstance(obj, Series):
        #    result = result[0]
        return result


class GetConnection(Func):
    """
    Функция получения соединения с источником.
    Используется на уровне интерпретатора.
    """
    group = 'context'
    description = 'Функция контекста'
    args_description = [
        NonMandatoryArg('connections', 0),
        MandatoryArg('source_id', 1),
    ]

    @classmethod
    def get_name(cls):
        return 'connection'

    def _operation(self, *args):
        return args[0][args[1]]


_context_funcs = {
    GetFromContext.get_name(): GetFromContext,
    GetSlice.get_name(): GetSlice,
    GetConnection.get_name(): GetConnection,
}