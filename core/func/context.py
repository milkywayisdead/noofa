from pandas import Series

from .values import Variable
from .base import Func, MandatoryArg, NonMandatoryArg
from .errors import (
    InterpreterContextError, 
    ValueNotInContextError,
    RecursiveEvaluationError,
)


class Context:
    """
    Контекст интерпретатора.
    """
    def __init__(self, **kwargs):
        self.global_context = {**kwargs}  # глобальный контекст (весь отчёт)
        self.local_context = {}  #  локальный контекст (в случае выч. значения в строке или столбце)
        self._current_context = self.global_context
        self._using_local = False
        self._values = {}  # вычисляемые значения

        #  используем "стэк" для контроля рекурсивных вычислений
        self._values_stack = []

    def add_values(self, values_list, evaluator):
        """
        Добавление значений в контекст.
        values_list - список словарей с ключами name и value,
        evaluator - объект-вычислитель.
        """
        for v in values_list:
            name, value = v['name'], v['value']
            self._values[name] = Variable(name, value, evaluator)

    def get_value(self, name):
        """
        Получение значения.
        """
        #  если значение уже вычисляется и какое-либо из значений, от которых
        #  оно зависит, требуют вычисления этого же значения, то выбрасываем ошибку по рекурсии
        if name in self._values_stack:
            self._values_stack.clear()  # очищаем "стэк" в случае ошибки по рекурсии
            raise RecursiveEvaluationError(name)
        try:
            value_obj = self._values[name]
        except KeyError:
            raise ValueNotInContextError(name)

        #  добавляем название значения в "стэк"
        self._values_stack.append(name)

        value = value_obj.evaluate()

        #  при успешном получении значения убираем название из "стэка"
        self._values_stack.pop()

        return value

    def update_value(self, name, value):
        """
        Обновление значения.
        """
        if name in self._values:
            self._values[name].force_set(value)

    def clear_local(self):
        self.local_context = {}

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


class GetValue(Func):
    """
    Функция получения значения из контекста интерпретатора.
    Используется на уровне интерпретатора для получения вычисляемых значений.
    """
    group = 'context'
    description = 'Функция контекста'
    args_description = [
        MandatoryArg('context', 0),
        MandatoryArg('var', 1),
    ]

    @classmethod
    def get_name(cls):
        return 'get_value'

    def _operation(self, *args):
        ctx, name = args[0], args[1]
        return ctx.get_value(name)


class GetFromContext(Func):
    """
    Функция получения значения из контекста интерпретатора.
    Используется на уровне интерпретатора для получения датафреймов.
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
        return result


class GetConnection(Func):
    """
    Функция получения соединения с источником.
    Используется на уровне интерпретатора.
    """
    group = 'context'
    description = 'Функция контекста'
    args_description = [
        MandatoryArg('context', 0),
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
    GetValue.get_name(): GetValue,
}
