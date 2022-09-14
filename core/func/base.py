from .errors import NotEnoughArguments


class Func:
    """
    Базовая функция.
    """
    description = '__'  # описание функции    
    args_description = []  #  описание аргументов
    group = 'str'  # группа, к которой относится функция (математическая, строковая и пр.)
    operation = None  # функция, которая будет выполняться

    def __init__(self, *args):
        self._args = [arg for arg in args]  # переданные аргументы
        self._mandatory = 0
        for arg in self.__class__.args_description:
            if arg.is_mandatory:
                self._mandatory += 1

    @classmethod
    def get_name(cls):
        return cls.__name__.lower()

    @classmethod
    def get_description(cls):
        """
        Описание функции.
        """
        return cls.description

    @classmethod
    def get_group(cls):
        """
        Группа, к которой относится функция.
        """
        return cls.group

    def _operation(self, *args):
        """
        Функция, которая будет выполняться,
        если operation класса is None.
        """
        pass

    def _get_operation(self):
        """
        Функция, которая будет выполняться.
        """
        cls_op = self.__class__.operation
        if cls_op is not None:
            return cls_op
        else:
            return self._operation

    def __call__(self):
        operation = self._get_operation()
        args_len = len(self._args)
        if args_len < self._mandatory:
            raise NotEnoughArguments(self.get_name(), self._mandatory)
        args = []
        for arg in self._args:
            if issubclass(type(arg), Func):
                args.append(arg())
            else:
                args.append(arg)
        return operation(*args)


class MathFunc(Func):
    """
    Математическая функция.
    """
    group = 'math'


class StrFunc(Func):
    """
    Функция для работы со строками.
    """
    group = 'str'


class DateFunc(Func):
    """
    Функция для работы с датой и временем.
    """
    group = 'date'


class LogicFunc(Func):
    """
    Логическая функция.
    """
    group = 'logic'


class TypeconvFunc(Func):
    """
    Функция преобразования типа.
    """
    group = 'typeconv'


class DatastructFunc(Func):
    """
    Функция для работы со структурами данных.
    """
    group = 'datastruct'


class Operator(Func):
    """
    Функции-операторы.
    """
    group = 'operators'
    sign = None

    @property
    def sign(self):
        return self.__class__.sign


class DataframeFunc(Func):
    """
    Функции для работы с датафреймами.
    """
    group = 'dataframe'


class SqlFunc(Func):
    """
    Функции select-запросов.
    """
    group = 'sql'


class StatisticsFunc(Func):
    """
    Статистические функции.
    """
    group = 'statistics'


class ConnectionFunc(Func):
    """
    Функции подключения к источникам.
    """
    group = 'connection'


class NonMandatoryArg:
    """
    Необязательный аргумент функции.
    """
    mandatory = False  # обязательный ли аргумент

    def __init__(self, name, index):
        self._name = name  # название
        self._index = index  # порядковый номер в списке аргументов

    @property
    def name(self):
        return self._name

    @property
    def is_mandatory(self):
        """
        Обязательный ли аргумент.
        """
        return self.__class__.mandatory


class MandatoryArg(NonMandatoryArg):
    """
    Обязательный аргумент.
    """
    mandatory = True