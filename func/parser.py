"""
Парсинг функций и формул.
"""

import re
from abc import ABC, abstractmethod


class Rule(ABC):
    """
    Абстрактное правило.
    """
    @abstractmethod
    def match(self, token):
        pass

    @abstractmethod
    def scan(self, token_stream, *args):
        pass

    @property
    @abstractmethod
    def type(self):
        return


class SymbolRule(Rule):
    """
    Правило для символов.
    """
    def match(self, token):
        if re.match('[a-zA-Z_]', token):
            return True

    def scan(self, token_stream, *args):
        res = args[0]
        c = token_stream.next
        while c is not None and re.match(self.scan_re, c):
            res += token_stream.get_next()
            c = token_stream.next
        return res

    @property
    def scan_re(self):
        return '[a-zA-Z_]'

    @property
    def type(self):
        return 'symbol'


class StringRule(Rule):
    """
    Правило для строк.
    """
    def match(self, token):
        if token in ['"', "'"]:
            return True

    def scan(self, token_stream, *args):
        delimiter = args[0]
        res = ""
        while token_stream.next != delimiter:
            c = token_stream.get_next()
            if c is None:
                raise Exception('Конец кода формулы')
            res += c
        token_stream.get_next()
        return res

    @property
    def scan_re(self):
        return

    @property
    def type(self):
        return 'string'


class NumberRule(Rule):
    """
    Правило для чисел.
    """
    def match(self, token):
        if re.match('[0-9.]', token):
            return True

    def scan(self, token_stream, *args):
        res = args[0]
        c = token_stream.next
        while c is not None and re.match(self.scan_re, c):
            res += token_stream.get_next()
            c = token_stream.next
        return res

    @property
    def scan_re(self):
        return '[0-9.]'

    @property
    def type(self):
        return 'number'


class OperatorRule(Rule):
    """
    Правило для операторов.
    """
    def match(self, token):
        if token in ['+', '-', '*', '/']:
            return True

    def scan(self, token_stream, *args):
        return args[0]

    @property
    def scan_re(self):
        return

    @property
    def type(self):
        return 'operator'


class TokenStream:
    """
    Поток токенов.
    """
    def __init__(self, tokens):
        self._stream = iter(tokens)
        self._next = None
        self.set_next()

    def set_next(self):
        try:
            self._next = next(self._stream)
        except StopIteration:
            self._next = None

    def get_next(self):
        n = self.next
        self.set_next()
        return n

    @property
    def next(self):
        return self._next


class FormulaLexer:
    """
    Лексер для функций и формул.
    """
    def __init__(self, tokens):
        self._rules = [
            SymbolRule(),
            OperatorRule(),
            StringRule(),
            NumberRule()
        ]

        self._stream = TokenStream(tokens)

    def lex(self):
        stream = self._stream
        while stream.next is not None:
            token = stream.get_next()
            if token == ' \n':
                pass
            for rule in self._rules:
                if rule.match(token):
                    yield (rule.type, rule.scan(stream, token))
                continue
            
