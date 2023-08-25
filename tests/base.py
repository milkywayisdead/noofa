import unittest

from noofa.core.func.interpreter import Interpreter
from noofa.core.func.errors import NotEnoughArguments as NEA
from noofa.core.func.errors import ArgumentTypeError as ATE


class NoofaTest(unittest.TestCase):
    @property
    def is_noofa(self):
        return True

    @classmethod
    def suite(cls):
        return unittest.makeSuite(cls)


class NoofaSuite(unittest.TestSuite):
    def add(self, test_component):
        is_noofa_test = False
        try:
            is_noofa_test = test_component.is_noofa
        except AttributeError:
            pass
        if is_noofa_test:
            self.addTest(test_component.suite())
        else:
            _ = test_component
            if isinstance(test_component, unittest.TestCase):
                _ = unittest.makeSuite(test_component)
            self.addTest(_)


class NoofaRunner(unittest.TextTestRunner):
    pass


class NoofaInterpreterTest(NoofaTest):
    @classmethod
    def set_up_interpreter(cls):
        cls.interpreter = Interpreter()

    def evaluate(self, expression):
        return self.interpreter.evaluate(expression)


class NoofaFunctionTest(NoofaTest):
    @classmethod
    def add_cases_from_list(cls, cases=[]):
        cls.cases = FunctionCase.from_list(cases)

    def test_functionality(self):
        for fc in self.cases:
            cases = fc.get_subcases()
            for case in cases:
                try:
                    f, expected, assertion = case
                except ValueError:
                    f, expected = case
                    assertion = 'equal'

                msg = fc.func.get_name()
                with self.subTest(msg):
                    if assertion == 'equal':
                        self.assertEqual(f(), expected)
                    elif assertion == 'isinstance':
                        self.assertIsInstance(f(), expected)

    def test_nea(self):
        for fc in self.cases:
            case = fc.nea_case
            if case is None:
                continue
            with self.subTest():
                self.assertRaises(NEA, case)

    def test_ate(self):
        for fc in self.cases:
            for case in fc.ate_cases:
                with self.subTest(case):
                    self.assertRaises(ATE, case)


class FunctionCase:
    def __init__(self, func, subcases=(), ate=(), nea_args=()):
        self.func = func
        self.subcases = subcases
        self.nea_args = nea_args
        self.ate = ate

    def get_subcases(self):
        cases = []
        for sc in self.subcases:
            args, expected = sc[0], sc[1]
            try:
                assertion = sc[2]
            except IndexError:
                assertion = 'equal'
            if not isinstance(args, tuple):
                args = (args, )
            cases.append((self.func(*args), expected, assertion))
        return cases

    @property
    def nea_case(self):
        if self.nea_args is not None:
            return self.func(*self.nea_args)

    @property
    def ate_cases(self):
        ate_cases = []
        for args in self.ate:
            if not isinstance(args, tuple):
                args = (args, )
            ate_cases.append(self.func(*args))
        return ate_cases

    @classmethod
    def from_list(cls, cases):
        return [cls(*case) for case in cases]
