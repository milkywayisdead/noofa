from .base import Func


def _contains(string, sub):
    return sub in string

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


class Contains(Func):
    """
    Содержит ли строка другую строку.
    """
    operation = _contains
    operands_num = 2
    unpack_values = True


class Endswith(Func):
    """
    Заканчивается ли строка другой строкой.
    """
    operation = _endswith
    operands_num = 2
    unpack_values = True


class Len(Func):
    """
    Получение длины строки.
    """
    operation = len
    operands_num = 1


class Lower(Func):
    """
    Перевод строки в нижний регистр.
    """
    operation = _lower
    operands_num = 1


class Upper(Func):
    """
    Перевод строки в верхний регистр.
    """
    operation = _upper
    operands_num = 1


class Concat(Func):
    """
    Сложение строк.
    """
    operation = _concat
    operands_num = -1
    unpack_values = True


class Join(Func):
    """
    Объединение строк по разделителю.
    """
    operation = _join
    operands_num = 2
    unpack_values = True


class Startswith(Func):
    """
    Начинается ли строка с другой строки.
    """
    operation = _startswith
    operands_num = 2
    unpack_values = True