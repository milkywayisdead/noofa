from pandas import DataFrame

from noofa.tests.base import NoofaTest, NoofaInterpreterTest
from noofa.core.func import operators as O
from noofa.core.func.errors import (
    NotEnoughArguments,
    ArgumentTypeError,
    ExpressionParsingError,
    ExpressionSyntaxError,
    InterpreterContextError,
)


class TestInterpreter(NoofaInterpreterTest):
    """
    Тестирование интерпретатора выражений.
    """
    @classmethod
    def setUpClass(cls):
        cls.set_up_interpreter()

    def test_int(self):
        self.assertEqual(self.evaluate('5'), 5)

    def test_float(self):
        self.assertEqual(self.evaluate('5.6'), 5.6)
        self.assertEqual(self.evaluate('.6'), 0.6)

    def test_negative_number(self):
        self.assertEqual(self.evaluate('-5'), -5)
        self.assertEqual(self.evaluate('(-5)'), -5)

    def test_str(self):
        self.assertEqual(self.evaluate('"hello"'), 'hello')
        self.assertEqual(self.evaluate("'hello'"), 'hello')

    def test_and_or_priority(self):
        self.assertFalse(self.evaluate('false() | true() & false()'))

    def test_eq_neq_and_priority(self):
        self.assertTrue(self.evaluate('1 == 1 & 1 != 2'))

    def test_gt_gte_and_priority(self):
        self.assertFalse(self.evaluate('1 >= 2 & 2 > 1'))

    def test_lt_lte_and_priority(self):
        self.assertFalse(self.evaluate('1 <= 2 & 2 < 1'))

    def test_gt_gte_lt_lte_priority(self):
        self.assertTrue(self.evaluate('1 <= 2 & 2 > 1'))
        self.assertTrue(self.evaluate('2 >= 1 & 1 < 2'))

    def test_arithm_comparison_priority(self):
        self.assertTrue(self.evaluate('2 * 2 >= 3 + 1'))
        self.assertTrue(self.evaluate('6 - 3 <= 4 - 1'))

    def test_arithm_priority(self):
        self.assertEqual(self.evaluate('1 + 1 - 4'), -2)
        self.assertEqual(self.evaluate('1 - 4 + 1'), -2)
        self.assertEqual(self.evaluate('2 + 3 * 5'), 17)
        self.assertEqual(self.evaluate('(2 + 3) * 5'), 25)
        self.assertEqual(self.evaluate('2 + 3 / 5'), 2.6)
        self.assertEqual(self.evaluate('(2 + 3) / 5'), 1)
        self.assertEqual(self.evaluate('2 * 5 + 3'), 13)
        self.assertEqual(self.evaluate('6 * 2 / 4'), 3)
        self.assertEqual(self.evaluate('6 / 2 * 4'), 12)

    def test_value_not_found(self):
        self.assertRaises(InterpreterContextError, self.evaluate, 'non_existent_value')

    def test_function_not_found(self):
        self.assertRaises(Exception, self.evaluate, 'non_existent_function()')

    def test_syntax(self):
        cases = [
            '1..2',
            '==1',
            '!=1',
            '>=1',
            '>1',
            '<1',
            '<=1',
            '*1',
            '/1',
            '**',
            '//',
            '()',
        ]
        for case in cases:
            with self.subTest(i=case):
                self.assertRaises(
                    ExpressionSyntaxError,
                    self.evaluate,
                    case
                )

    def test_parsing_errors(self):
        cases = [
            ',',
            '!',
            '?',
            '"',
            '1 = 1',
        ]
        for case in cases:
            with self.subTest(i=case):
                self.assertRaises(
                    ExpressionParsingError,
                    self.evaluate,
                    case
                )

    def test_parethesis(self):
        self.assertEqual(self.evaluate('(1 + 2) * 3'), 9)

    def test_no_opening_parenthesis(self):
        self.assertRaises(ExpressionParsingError, self.evaluate, '1 + 2)')

    def test_no_closing_parenthesis(self):
        self.assertRaises(ExpressionParsingError, self.evaluate, '(1 + 2')


class TestOperators(NoofaInterpreterTest):
    """
    Тестирование операторов интерпретатора выражений.
    """
    @classmethod
    def setUpClass(cls):
        cls.set_up_interpreter()

    def test_add(self):
        self.assertEqual(self.evaluate('1 + 1'), 2)

    def test_add_df(self):
        self.assertIsInstance(self.evaluate('dataframe() + dataframe()'), DataFrame)

    def test_subtract(self):
        self.assertEqual(self.evaluate('1 - 1'), 0)

    def test_negative_number(self):
        self.assertEqual(self.evaluate('-1'), -1)
        self.assertEqual(self.evaluate('-1 - 1'), -2)

    def test_multiply(self):
        self.assertEqual(self.evaluate('2 * 3'), 6)

    def test_divide(self):
        self.assertEqual(self.evaluate('6 / 3'), 2)

    def test_zero_division(self):
        self.assertRaises(ZeroDivisionError, self.evaluate, '6 / 0')

    def test_gt(self):
        self.assertTrue(self.evaluate('2 > 1'))
        self.assertFalse(self.evaluate('1 > 2'))

    def test_gte(self):
        self.assertTrue(self.evaluate('2 >= 1'))
        self.assertTrue(self.evaluate('2 >= 2'))
        self.assertFalse(self.evaluate('1 >= 2'))

    def test_lt(self):
        self.assertTrue(self.evaluate('1 < 2'))
        self.assertFalse(self.evaluate('2 < 1'))

    def test_lte(self):
        self.assertTrue(self.evaluate('1 <= 2'))
        self.assertTrue(self.evaluate('1 <= 1'))
        self.assertFalse(self.evaluate('2 <= 1'))

    def test_eq(self):
        self.assertTrue(self.evaluate('1 == 1'))
        self.assertFalse(self.evaluate('1 == 2'))

    def test_neq(self):
        self.assertFalse(self.evaluate('1 != 1'))
        self.assertTrue(self.evaluate('1 != 2'))

    def test_and(self):
        self.assertTrue(self.evaluate('true() & true()'))
        self.assertFalse(self.evaluate('true() & false()'))
        self.assertFalse(self.evaluate('false() & false()'))

    def test_or(self):
        self.assertTrue(self.evaluate('true() | true()'))
        self.assertTrue(self.evaluate('true() | false()'))
        self.assertFalse(self.evaluate('false() | false()'))


class TestOperatorsClasses(NoofaTest):
    """
    Тестирование классов операторов.
    """
    def test_add(self):
        op = O.Add(1, 2)
        self.assertEqual(op(), 3)

    def test_add_raises_nea(self):
        op = O.Add(2)
        self.assertRaises(NotEnoughArguments, op)

    def test_add_raises_ate(self):
        op = O.Add(2, None)
        self.assertRaises(ArgumentTypeError, op)

    def test_add_df(self):
        op = O.Add(DataFrame(), DataFrame())
        self.assertIsInstance(op(), DataFrame)

    def test_subtract(self):
        op = O.Subtract(3, 1)
        self.assertEqual(op(), 2)

    def test_subtract_raises_nea(self):
        op = O.Subtract(2)
        self.assertRaises(NotEnoughArguments, op)

    def test_subtract_raises_ate(self):
        op = O.Subtract(2, None)
        self.assertRaises(ArgumentTypeError, op)

    def test_subtract_returns_negative(self):
        op = O.Subtract(None, 2)
        self.assertEqual(op(), -2)

    def test_mult(self):
        op = O.Multiply(3, 2)
        self.assertEqual(op(), 6)

    def test_mult_raises_nea(self):
        op = O.Multiply()
        self.assertRaises(NotEnoughArguments, op)

    def test_mult_raises_ate(self):
        op = O.Multiply(2, DataFrame())
        op2 = O.Multiply(2, '2')
        self.assertRaises(ArgumentTypeError, op)
        self.assertRaises(ArgumentTypeError, op2)

    def test_divide(self):
        op = O.Divide(6, 2)
        self.assertEqual(op(), 3)

    def test_divide_raises_nea(self):
        op = O.Divide(6)
        self.assertRaises(NotEnoughArguments, op)

    def test_divide_raises_ate(self):
        op = O.Divide(2, DataFrame())
        op2 = O.Divide(2, '2')
        self.assertRaises(ArgumentTypeError, op)
        self.assertRaises(ArgumentTypeError, op2)

    def test_gt(self):
        op1 = O.IsGt(2, 1)
        op2 = O.IsGt(1, 2)
        self.assertTrue(op1())
        self.assertFalse(op2())

    def test_gt_raises_nea(self):
        op = O.IsGt(6)
        self.assertRaises(NotEnoughArguments, op)

    def test_gt_raises_ate(self):
        op1 = O.IsGt(DataFrame(), 2)
        op2 = O.IsGt(2, '2')
        self.assertRaises(ArgumentTypeError, op1)
        self.assertRaises(ArgumentTypeError, op2)

    def test_gte(self):
        op1 = O.IsGte(2, 1)
        op2 = O.IsGte(1, 2)
        op3 = O.IsGte(1, 1)
        self.assertTrue(op1())
        self.assertFalse(op2())
        self.assertTrue(op3())

    def test_gte_raises_nea(self):
        op = O.IsGte(6)
        self.assertRaises(NotEnoughArguments, op)

    def test_gte_raises_ate(self):
        op1 = O.IsGte(DataFrame(), 2)
        op2 = O.IsGte(2, '2')
        self.assertRaises(ArgumentTypeError, op1)
        self.assertRaises(ArgumentTypeError, op2)

    def test_lt(self):
        op1 = O.IsLt(1, 2)
        op2 = O.IsLt(2, 1)
        self.assertTrue(op1())
        self.assertFalse(op2())

    def test_lt_raises_nea(self):
        op = O.IsLt(6)
        self.assertRaises(NotEnoughArguments, op)

    def test_lt_raises_ate(self):
        op1 = O.IsLt(DataFrame(), 2)
        op2 = O.IsLt(2, '2')
        self.assertRaises(ArgumentTypeError, op1)
        self.assertRaises(ArgumentTypeError, op2)

    def test_lte(self):
        op1 = O.IsLte(1, 2)
        op2 = O.IsLte(2, 1)
        op3 = O.IsLte(1, 1)
        self.assertTrue(op1())
        self.assertFalse(op2())
        self.assertTrue(op3())

    def test_lte_raises_nea(self):
        op = O.IsLte(6)
        self.assertRaises(NotEnoughArguments, op)

    def test_lte_raises_ate(self):
        op1 = O.IsLte(DataFrame(), 2)
        op2 = O.IsLte(2, '2')
        self.assertRaises(ArgumentTypeError, op1)
        self.assertRaises(ArgumentTypeError, op2)

    def test_eq(self):
        op1 = O.IsEq(1, 2)
        op2 = O.IsEq(1, 1)
        self.assertFalse(op1())
        self.assertTrue(op2())

    def test_eq_raises_nea(self):
        op = O.IsEq(1)
        self.assertRaises(NotEnoughArguments, op)

    def test_eq_raises_ate(self):
        op = O.IsEq(DataFrame(), 2)
        self.assertRaises(ArgumentTypeError, op)

    def test_neq(self):
        op1 = O.IsNeq(1, 2)
        op2 = O.IsNeq(1, 1)
        self.assertTrue(op1())
        self.assertFalse(op2())

    def test_neq_raises_nea(self):
        op = O.IsNeq(1)
        self.assertRaises(NotEnoughArguments, op)

    def test_neq_raises_ate(self):
        op = O.IsNeq(DataFrame(), 2)
        self.assertRaises(ArgumentTypeError, op)

    def test_and(self):
        op1 = O.And(True, False)
        op2 = O.And(True, True)
        op3 = O.And(False, False)
        self.assertFalse(op1())
        self.assertTrue(op2())
        self.assertFalse(op3())

    def test_and_raises_nea(self):
        op = O.And(True)
        self.assertRaises(NotEnoughArguments, op)

    def test_or(self):
        op1 = O.Or(True, False)
        op2 = O.Or(True, True)
        op3 = O.Or(False, False)
        self.assertTrue(op1())
        self.assertTrue(op2())
        self.assertFalse(op3())

    def test_or_raises_nea(self):
        op = O.Or(True)
        self.assertRaises(NotEnoughArguments, op)
