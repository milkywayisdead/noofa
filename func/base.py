class Func:
    """
    Базовая функция.
    """
    description = 'Функция, которая ничего не делает'  # описание функции

    #  описание аргументов
    args_description = [
        {'name': 'arg0', 'index': 0, 'is_mandatory': True},
        {'name': 'arg1', 'index': 1, 'is_mandatory': True},
        {'name': 'arg2', 'index': 2, 'is_mandatory': False, 'default': 1},
    ]

    group = 'str'  # группа, к которой относится функция (математическая, строковая и пр.)
    operation = None  # функция, которая будет выполняться

    def __init__(self, *args):
        self._args = [arg for arg in args]  # переданные аргументы
        self._mandatory = 0
        for arg in self.__class__.args_description:
            if arg['is_mandatory']:
                self._mandatory += 1

    @property
    def description(self):
        """
        Описание функции.
        """
        return self.__class__.description

    @property
    def group(self):
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
        if args_len < self._mandatory:
            return '#ERROR'
        try:
            args = []
            for arg in self._args:
                if issubclass(type(arg), Func):
                    args.append(arg())
                else:
                    args.append(arg)
            result = operation(*args)
        except Exception as e:
            print(e)
            return '#ERROR'
        else:
            return result


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
