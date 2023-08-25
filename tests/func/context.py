from noofa.tests.base import NoofaInterpreterTest
from noofa.core.func.errors import (
    InterpreterContextError,
    ValueNotInContextError,
    RecursiveEvaluationError,
)


class TestContext(NoofaInterpreterTest):
    """
    Тестирование контекста интерпретатора.
    """
    @classmethod
    def setUpClass(cls):
        cls.set_up_interpreter()
        cls.nonex_value = 'non_existent_value'
        cls.ex_value = 'x'
        cls.value = 5
        cls.local_value = 4

    def tearDown(self):
        self.interpreter._context._values = {}
        self.interpreter._context.clear_local()
        self.interpreter._context.global_context = {}
        self.interpreter._context.switch_to_global()

    def test_var_not_found(self):
        self.assertRaises(
            InterpreterContextError,
            self.evaluate,
            self.nonex_value
        )

    def test_global_var(self):
        self.interpreter.add_to_global(
            self.ex_value,
            self.value
        )

        self.interpreter._context.switch_to_global()
        gv = self.evaluate(self.ex_value)
        self.assertEqual(gv, self.value)

    def test_local_var(self):
        self.interpreter.add_to_local(
            self.ex_value,
            self.local_value
        )

        self.interpreter._context.switch_to_local()
        lv = self.evaluate(self.ex_value)
        self.assertEqual(lv, self.local_value)

    def test_global_and_local(self):
        self.interpreter.add_to_global(
            self.ex_value,
            self.value
        )
        self.interpreter.add_to_local(
            self.ex_value,
            self.local_value
        )
        self.interpreter._context.switch_to_global()
        gv = self.evaluate(self.ex_value)
        self.interpreter._context.switch_to_local()
        lv = self.evaluate(self.ex_value)

        self.assertEqual(gv, self.value)
        self.assertEqual(lv, self.local_value)
        self.assertNotEqual(gv, lv)

    def test_value(self):
        self.interpreter.add_values(
            [{'name': self.ex_value, 'value': str(self.value)}],
            self.interpreter
        )
        self.assertEqual(
            self.evaluate(f'get_value("{self.ex_value}")'),
            self.value
        )
        self.assertEqual(
            self.interpreter.get_value(self.ex_value),
            self.value
        )

    def test_recursive_evaluation(self):
        expr = f'get_value("{self.ex_value}")'
        self.interpreter.add_values(
            [{'name': self.ex_value, 'value': expr}],
            self.interpreter
        )
        self.assertRaises(
            RecursiveEvaluationError,
            self.evaluate,
            expr
        )

    def test_non_existent_value(self):
        self.assertRaises(
            ValueNotInContextError,
            self.evaluate,
            f'get_value("{self.nonex_value}")'
        )
