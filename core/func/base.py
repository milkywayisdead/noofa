from .errors import NotEnoughArguments, ArgumentTypeError


class Func:
    """
    Базовая функция.
    """
    description = '__'  # описание функции
    args_description = []  #  описание аргументов
    group = 'str'  # группа, к которой относится функция (математическая, строковая и пр.)
    operation = None  # функция, которая будет выполняться

    """
    Признак того, что функция принимает аргументы одного типа.
    При None не производится проверка аргументов на соответствие этому типу.
    Если атрибут не None, то производится проверка сооветствия всех аргументов
    этому типу.
    """
    _arguments_type = None

    def __init__(self, *args):
        self._args = [arg for arg in args]  # переданные аргументы
        self._mandatory = 0
        for arg in self.__class__.args_description:
            if arg.is_mandatory:
                self._mandatory += 1

    @classmethod
    def get_func_info(cls):
        args = []
        for arg in cls.args_description:
            _ = ''
            if not arg.is_mandatory:
                _ = ' (необяз.)'
            args.append(f'{arg.name}{_}')

        name = cls.get_name()
        return {
            'group': cls.group,
            'name': name,
            'description': cls.get_description(),
            'args': args,
            'as_str': f'{name}({",".join(args)})',
        }

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

    @property
    def arguments_type(self):
        return self.__class__._arguments_type

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

        # проверка количества аргументов
        args_len = len(self._args)
        if args_len < self._mandatory:
            raise NotEnoughArguments(self.get_name(), self._mandatory)

        args = []
        for arg in self._args:
            if issubclass(type(arg), Func):
                args.append(arg())
            else:
                args.append(arg)

        # проверка типов аргументов
        if self.arguments_type is not None:
            arg_check = self._check_one_type_arguments
        else:
            arg_check = self._check_arguments
        arg_check(args)

        return operation(*args)

    def _check_arguments(self, arguments):
        args_desc = self.__class__.args_description
        for ind, value in enumerate(arguments):
            try:
                arg = args_desc[ind]
            except IndexError:
                break
            is_valid = arg.check_value(value)
            if not is_valid:
                type_ = value.__class__.__name__
                raise ArgumentTypeError(self.get_name(), type_)
        return True

    def _check_one_type_arguments(self, arguments):
        arg_type = self.arguments_type
        for arg in arguments:
            if not isinstance(arg, arg_type):
                type_ = arg.__class__.__name__
                raise ArgumentTypeError(self.get_name(), type_)
        return True


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
    _arguments_type = str


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

    def __init__(self, name, index, types=[]):
        self._name = name  # название
        self._index = index  # порядковый номер в списке аргументов
        self._types = types  # список допустимых типов аргумента

    @property
    def name(self):
        return self._name

    @property
    def is_mandatory(self):
        """
        Обязательный ли аргумент.
        """
        return self.__class__.mandatory

    def check_value(self, value):
        """
        Проверка значения на соответствие одному из допустимых типов.
        Возвращает True, если значение относится к одному из допустимых типов.
        При пустом списке типов (self._types) возвращается True, т.е. тип аргумента
        может быть любым.
        """
        type_is_ok = False
        if self._types == []:
            return True
        for type_ in self._types:
            if isinstance(value, type_):
                type_is_ok = True
                break
        return type_is_ok


class MandatoryArg(NonMandatoryArg):
    """
    Обязательный аргумент.
    """
    mandatory = True
