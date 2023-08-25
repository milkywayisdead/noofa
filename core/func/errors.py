class ExpressionParsingError(Exception):
    pass


class ExpressionSyntaxError(Exception):
    def __str__(self):
        return 'Ошибка синтаксиса'


class ExpressionEvaluationError(Exception):
    pass


class NotEnoughArguments(Exception):
    def __init__(self, fname, mandatory):
        self._fname = fname
        self._mandatory = mandatory

    def __str__(self):
        return f'Функции {self._fname} требуется минимум {self._mandatory} аргументов'


class ArgumentTypeError(Exception):
    def __init__(self, fname, arg_type):
        self._fname = fname
        self._arg_type = arg_type

    def __str__(self):
        return f'Функция {self._fname} не принимает аргументы типа {self._arg_type}'


class InterpreterContextError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'В контексте отсутствует элемент {self.key}'


class ValueNotInContextError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'В контексте отсутствует значение {self.key}'


class RecursiveEvaluationError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'Рекурсивное вычисление при получении значения {self.key}'
