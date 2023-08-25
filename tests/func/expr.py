import math
import statistics
from datetime import datetime, date, time
from pandas import DataFrame, Series

from noofa.tests.base import NoofaInterpreterTest


_df_expr = ''.join([
    'dataframe(',
    'list(',
    'list("a", "b", "c"),'
    'list(1,2,3),',
    'list(4,5,6)',
    ')',
    ')'
])


class TestFunctionsExpressions(NoofaInterpreterTest):
    """
    Тестирование функций интерпретатора в выражениях.
    """
    @classmethod
    def setUpClass(cls):
        cls.set_up_interpreter()
        cls.math_eq_cases = _MATH_EQ_CASES
        cls.logic_eq_cases = _LOGIC_EQ_CASES
        cls.strings_eq_cases = _STRINGS_EQ_CASES
        cls.date_eq_cases = _DATE_EQ_CASES
        cls.conv_eq_cases = _CONV_EQ_CASES
        cls.ds_eq_cases = _DS_EQ_CASES
        cls.df_eq_cases = _DF_EQ_CASES
        cls.stats_eq_cases = _STATS_EQ_CASES
        cls.df_expr = _df_expr

    def test_equality_cases(self):
        for case in self.equality_cases:
            expression, expected = case
            with self.subTest(expression):
                res = self.evaluate(expression)
                self.assertEqual(res, expected)

    @property
    def equality_cases(self):
        cases = ()
        for case in [
            self.math_eq_cases,
            self.logic_eq_cases,
            self.strings_eq_cases,
            self.date_eq_cases,
            self.conv_eq_cases,
            self.ds_eq_cases,
            self.df_eq_cases,
        ]:
            cases += case
        return cases

    def test_dataframe(self):
        df = self.evaluate(self.df_expr)
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(df.shape, (2, 3))

    def test_date(self):
        d1 = self.evaluate('date()')
        d2 = datetime.now().date()
        self.assertEqual(d1, d2)

    def test_time(self):
        t = self.evaluate('time()')
        self.assertIsInstance(t, time)

    def test_now(self):
        n = self.evaluate('now()')
        self.assertIsInstance(n, datetime)


"""
Кейсы для проверки равенства результата ввыражения и ожидаемого значения.
Первый элемент в кортежах - выражение, второй - ожидаемый результат.
"""
_MATH_EQ_CASES = (
    ('abs(-1)', 1),
    ('abs(1)', 1),
    ('acos(1)', math.acos(1)),
    ('asin(1)', math.asin(1)),
    ('atan(1)', math.atan(1)),
    ('ceil(3.14)', 4),
    ('floor(3.54)', 3),
    ('cos(1)', math.cos(1)),
    ('cot(1)', 1/math.tan(1)),
    ('degrees(1)', math.degrees(1)),
    ('radians(1)', math.radians(1)),
    ('div(9, 2)', 4.5),
    ('idiv(9, 2)', 4),
    ('exp(3)', math.exp(3)),
    ('ln(3)', math.log(3)),
    ('log(3, 5)', math.log(3, 5)),
    ('pow(3, 3)', 27),
    ('round(3.14)', 3),
    ('round(3.54)', 4),
    ('round(3.1415926, 2)', 3.14),
    ('sin(1)', math.sin(1)),
    ('cos(1)', math.cos(1)),
    ('sqrt(13)', math.sqrt(13)),
    ('sum(1)', 1),
    ('sum(1, 2, 3)', 6),
    ('sum(list(1, 2, 3))', 6),
    ('tan(1)', math.tan(1)),
)


_LOGIC_EQ_CASES = (
    ('true()', True),
    ('false()', False),
    ('eq(1, 2)', False),
    ('eq(2, 2)', True),
    ('neq(1, 2)', True),
    ('neq(2, 2)', False),
    ('gt(2, 1)', True),
    ('gt(1, 2)', False),
    ('gte(2, 1)', True),
    ('gte(2, 2)', True),
    ('gte(1, 2)', False),
    ('lt(2, 1)', False),
    ('lt(1, 2)', True),
    ('lte(2, 1)', False),
    ('lte(2, 2)', True),
    ('lte(1, 2)', True),
    ('if(true(), 1, 2)', 1),
    ('if(false(), 1, 2)', 2),
    ('and(true(), false())', False),
    ('and(true(), true())', True),
    ('or(true(), false())', True),
    ('or(true(), true())', True),
    ('or(false(), false())', False),
    ('in(1, list())', False),
    ('in(1, list(1, 2, 3))', True),
    ('switch(1, 0, list(1, 10), list(2, 20))', 10),
    ('switch(2, 0, list(1, 10), list(2, 20))', 20),
    ('switch(3, 0, list(1, 10), list(2, 20))', 0),
    ('switch(1, 0)', 0),
)


_STRINGS_EQ_CASES = (
    ('contains("12", "1")', True),
    ('contains("12", "3")', False),
    ('endswith("abc", "bc")', True),
    ('endswith("abc", "bce")', False),
    ('startswith("abc", "ab")', True),
    ('startswith("abc", "bc")', False),
    ('len("abc")', 3),
    ('lower("ABC")', 'abc'),
    ('upper("abc")', 'ABC'),
    ('concat("a", "b")', 'ab'),
    ('concat("a", "b", "c", "d")', 'abcd'),
    ('join(",", "a", "b")', "a,b"),
    ('join(", ", "a", "b", "c")', "a, b, c"),
)


_DATE_EQ_CASES = (
    ('sectodate(12345)', datetime(1970, 1, 1, 3, 25, 45)),
    ('msectodate(12345000)', datetime(1970, 1, 1, 3, 25, 45)),
    ('sectodatestr(12345)', '1970-01-01 03:25:45'),
    ('sectodatestr(12345, "%H:%M:%S %d-%m-%Y")', '03:25:45 01-01-1970'),
    ('msectodatestr(12345000)', '1970-01-01 03:25:45'),
    ('msectodatestr(12345000, "%H:%M:%S %d-%m-%Y")', '03:25:45 01-01-1970'),
    ('datetosec(sectodate(12345))', 12345),
    ('datetostr(sectodate(12345))', '1970-01-01 03:25:45'),
    ('datetostr(sectodate(12345), "%H:%M:%S %d-%m-%Y")', '03:25:45 01-01-1970'),
    ('strtodate("1970-01-01 03:25:45")', datetime(1970, 1, 1, 3, 25, 45)),
    ('strtodate("03:25:45 01-01-1970", "%H:%M:%S %d-%m-%Y")', datetime(1970, 1, 1, 3, 25, 45)),
)


_CONV_EQ_CASES = (
    ('to_str(5)', '5'),
    ('to_str(3.14)', '3.14'),
    ('to_str("a")', 'a'),
    ('to_int(3.14)', 3),
    ('to_int(3)', 3),
    ('to_int("3")', 3),
    ('to_float(3.14)', 3.14),
    ('to_float(3)', 3.0),
    ('to_float("3.14")', 3.14),
    ('to_float(".5")', 0.5),
)


_DS_EQ_CASES = (
    ('list()', []),
    ('list(1, 2, 3)', [1, 2, 3]),
    (f'to_list(get_column({_df_expr}, "a"))', [1, 4]),
)


_DF_EQ_CASES = (
    (f'df_count({_df_expr})', 2),
    (f'df_count(df_head({_df_expr}, 1))', 1),
    (f'df_count(df_tail({_df_expr}, 1))', 1),
    (f'df_count(df_union({_df_expr}, {_df_expr}))', 4),
    (f'df_count(df_join({_df_expr}, {_df_expr}, "a", "a", "inner"))', 2),
    (''.join([
        'df_count(',
        f'filter({_df_expr}, df_filter("a", "==", 1))'
        ')'
    ]), 1),
    (''.join([
        'df_count(',
        'filter(',
        f'add_column({_df_expr}, "d", list(7, 8)),'
        'df_filter("d", "==", 7)',
        ')',
        ')'
    ]), 1),
)


_ = [1, 2, 3, 4, 5]
_l = 'list(1, 2, 3, 4, 5)'
_STATS_EQ_CASES = (
    ('mean(list(1, 2, 3, 4))', 2.5),
    ('min(list(1, 2, 3, 0, 5))', 0),
    ('max(list(1, 2, 3, 0, 5))', 5),
    ('mode(list(1, 2, 1, 2, 1))', 1),
    (f'median({_l})', statistics.median(_)),
    (f'stdev({_l})', statistics.stdev(_, 1)),
    (f'stdev({_l}, 0)', statistics.stdev(_, 0)),
    (f'variance({_l})', statistics.variance(_, 1)),
    (f'variance({_l}, 0)', statistics.variance(_, 0)),
)
