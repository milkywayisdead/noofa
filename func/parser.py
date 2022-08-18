"""
Парсинг функций и формул.
"""

import re
from abc import ABC, abstractmethod


def parse(formula_string):
    lexer = FormulaLexer(formula_string)
    tokens = [tok for tok in lexer.lex()]
    token_stream = Stream(tokens)
    parser = Parser(token_stream)
    stree = [tok for tok in parser.parse()]
    return stree


class Parser:
    """
    Парсер.
    """
    def __init__(self, token_stream, stop_at=';'):
        self._tokens = token_stream
        self._stop_at = stop_at

    @property
    def stop_at(self):
        return self._stop_at

    @property
    def tokens(self):
        return self._tokens

    def parse(self):
        while self.tokens.next is not None:
            e = self.next_expression(None)
            if e is not None:
                yield e
            self.tokens.get_next()

    def next_expression(self, prev):
        next_ = self.tokens.next
        type_, value = next_['type'], next_['value']
        if type_ in self.stop_at:
            return prev
        self.tokens.get_next()
        if type_ in ('number', 'string', 'symbol') and prev is None:
            return self.next_expression(next_)
        elif type_ == 'operator':
            nxt = self.next_expression(None)
            return self.next_expression({'type': 'operator', 'value': value, 'left': prev, 'right': nxt})
        elif type_ == '(':
            args = self._scan_args(func=prev)
            return self.next_expression({'type': 'call', 'function': prev, 'args': args})
        else:
            raise Exception(f'Неожиданный токен: {(type_, value)}')

    def _scan_args(self, sep=',', end=')', func=None):
        args = []
        type_ = self.tokens.next['type']
        if type_ == end:
            self.tokens.get_next()
        else:
            if func is None:
                stop_at = (end)
            else:
                stop_at = (sep, end)
            arg_parser = Parser(self.tokens, stop_at)
            while type_ != end:
                p = arg_parser.next_expression(None)
                if p is not None:
                    args.append(p)
                type_ = self.tokens.next['type']
                self.tokens.get_next()
        return args


class Stream:
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
    Лексер для формул.
    """
    def __init__(self, tokens):
        self._rules = [
            SymbolRule(),
            OperatorRule(),
            StringRule(),
            NumberRule(),
            ErrorRule(),
        ]

        self._stream = Stream(tokens)

    def lex(self):
        stream = self._stream
        while stream.next is not None:
            token = stream.get_next()
            if token in ' \n':
                pass
            elif token in '(),;':
                yield {'type': token, 'value': ''}
            for rule in self._rules:
                if rule.match(token):
                    yield {'type': rule.type, 'value': rule.scan(stream, token)}
                    break


class Rule(ABC):
    """
    Абстрактное правило.
    """
    @abstractmethod
    def match(self, token):
        pass

    @abstractmethod
    def scan(self, token_stream, token):
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

    def scan(self, token_stream, token):
        res = token
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

    def scan(self, token_stream, token):
        delimiter = token
        res = ""
        while token_stream.next != delimiter:
            c = token_stream.get_next()
            if c is None:
                raise Exception('Незавершённый идентификатор строки')
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

    def scan(self, token_stream, token):
        res = token
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
        if token in ['+', '-', '*', '/', '>', '<']:
            return True

    def scan(self, token_stream, token):
        return token

    @property
    def scan_re(self):
        return

    @property
    def type(self):
        return 'operator'
            

class ErrorRule(Rule):
    def match(self, token):
        if not re.match('[ \n0-9a-zA-Z_();.,+-/*]', token):
            raise Exception(f'Неизвестный токен: {token}')

    def scan(self, token_stream, token):
        pass

    @property
    def type(self):
        pass