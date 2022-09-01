from .base import Func, MandatoryArg


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
            return self.global_context[key]

    def remove(self, key):
        """
        Удаление из текущего контекста.
        """
        self._current_context.pop(key)


class GetFromContext(Func):
    """
    Функция получения значения из контекста интерпретатора.
    Используется на уровне интерпретатора, во "внешний мир" не выводить.
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
    Функция получения среза, столбца либо строки датафрейма.
    Используется на уровне интерпретатора, во "внешний мир" не выводить.
    """
    group = 'context'
    description = 'Функция контекста'
    args_description = [
        MandatoryArg('context', 0),
        MandatoryArg('var', 1),
    ]

    @classmethod
    def get_name(cls):
        return '_getslice'

    def _operation(self, *args):
        df, slice_ = args[0], args[1]
        return df[slice_]


_context_funcs = {
    GetFromContext.get_name(): GetFromContext,
    GetSlice.get_name(): GetSlice,
}