class Result:
    """
    Результат вычисления формулы.
    """
    is_bad = False

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def is_bad(self):
        return self.__class__.is_bad


class ErrorResult(Result):
    """
    Результат выполнения с ошибкой.
    """
    is_bad = True

    def __init__(self, value=None):
        super().__init__('#ERROR')


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

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def fdescription(self):
        """
        Описание функции.
        """
        return self.__class__.description

    @property
    def fgroup(self):
        """
        Группа, к которой относится функция.
        """
        return self.__class__.group

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
        # если аргументов недостаточно, то возвращается результат с ошибкой
        if args_len < self._mandatory:
            return ErrorResult()
        try:
            args = []
            for arg in self._args:
                # если аргумент - результат с ошибкой,
                # то возвращается этот же результат
                if isinstance(arg, ErrorResult):
                    return arg
                # если аргумент является функцией,
                # то сначала нужно получить её результат
                if issubclass(type(arg), Func):
                    args.append(arg())
                else:
                    # если аргумент - экз. результата,
                    # то сначала нужно получить значение результата
                    if isinstance(arg, Result):
                        arg = arg.value
                    args.append(arg)
            result = operation(*args)
        except Exception as e:
            return ErrorResult()
        else:
            return Result(result)


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


class DataframeFunc(Func):
    """
    Функция для работы с датафреймами.
    """
    group = 'df'


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