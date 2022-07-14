"""
Функции работы со строками.
"""

from .base import StrFunc


def _endswith(string, sub):
    return string.endswith(sub)

def _startswith(string, sub):
    return string.startswith(sub)

def _lower(string):
    return string.lower()

def _upper(string):
    return string.upper()

def _concat(*strings):
    s = ''
    for i in strings:
        s += f'{i}'
    return s

def _join(string, substrings):
    return f'{string}'.join(substrings)


class Contains(StrFunc):
    """
    Содержит ли строка другую строку.
    """
    description = 'Проверка, содержит ли строка другую строку'
    args_description = [
        {'name': 'Строка1', 'index': 0, 'is_mandatory': True},
        {'name': 'Строка2', 'index': 1, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        return args[1] in args[0]


class Endswith(StrFunc):
    """
    Заканчивается ли строка другой строкой.
    """
    description = 'Проверка, заканчивается ли строка другой строкой'
    args_description = [
        {'name': 'Строка1', 'index': 0, 'is_mandatory': True},
        {'name': 'Строка2', 'index': 1, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        return args[0].endswith(args[1])


class Len(StrFunc):
    """
    Получение длины строки.
    """
    description = 'Получение длины строки'
    operation = len
    args_description = [
        {'name': 'Строка', 'index': 0, 'is_mandatory': True},
    ]


class Lower(StrFunc):
    """
    Перевод строки в нижний регистр.
    """
    description = 'Перевод строки в нижний регистр'
    args_description = [
        {'name': 'Строка', 'index': 0, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        return args[0].lower()


class Upper(StrFunc):
    """
    Перевод строки в верхний регистр.
    """
    description = 'Перевод строки в верхний регистр'
    args_description = [
        {'name': 'Строка', 'index': 0, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        return args[0].upper()


class Concat(StrFunc):
    """
    Сложение строк.
    """
    description = 'Сложение нескольких строк'
    args_description = [
        {'name': 'Строка1', 'index': 0, 'is_mandatory': True},
        {'name': 'Строка2', 'index': 1, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        result = ''
        for arg in args:
            result += arg
        return result


class Join(StrFunc):
    """
    Объединение строк по разделителю.
    """
    description = 'Объединение строк через разделитель'
    args_description = [
        {'name': 'Разделитель', 'index': 0, 'is_mandatory': True},
        {'name': 'Строка1', 'index': 1, 'is_mandatory': True},
        {'name': 'Строка2', 'index': 2, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        sep = args[0]
        subs = args[1:]
        return sep.join(subs)


class Startswith(StrFunc):
    """
    Начинается ли строка с другой строки.
    """
    description = 'Проверка, начинается ли строка другой строкой'
    args_description = [
        {'name': 'Строка1', 'index': 0, 'is_mandatory': True},
        {'name': 'Строка2', 'index': 1, 'is_mandatory': True},
    ]

    def _operation(self, *args):
        return args[0].startswith(args[1])