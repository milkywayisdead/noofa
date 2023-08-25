from noofa.tests.base import NoofaSuite, NoofaRunner
from noofa.tests.func.interpreter import (
    TestInterpreter,
    TestOperators,
    TestOperatorsClasses,
)
from noofa.tests.func.context import TestContext
from noofa.tests.func.math import TestMathFunctions
from noofa.tests.func.datastruct import TestDatastructFunctions
from noofa.tests.func.date import TestDateFunctions
from noofa.tests.func.typeconv import TestTypeConvFunctions
from noofa.tests.func.logic import TestLogicFunctions
from noofa.tests.func.strings import TestStringsFunctions
from noofa.tests.func.df import TestDfFunctions
from noofa.tests.func.sql import TestSqlFunctions
from noofa.tests.func.statistics import TestStatisticsFunctions
from noofa.tests.func.expr import TestFunctionsExpressions


def func_suite():
    suite = NoofaSuite()
    suite.add(TestOperators)
    suite.add(TestOperatorsClasses)
    suite.add(TestInterpreter)
    suite.add(TestContext)
    suite.add(TestMathFunctions)
    suite.add(TestDatastructFunctions)
    suite.add(TestDateFunctions)
    suite.add(TestTypeConvFunctions)
    suite.add(TestLogicFunctions)
    suite.add(TestStringsFunctions)
    suite.add(TestSqlFunctions)
    suite.add(TestStatisticsFunctions)
    suite.add(TestDfFunctions)
    suite.add(TestFunctionsExpressions)
    return suite


def run_tests():
    suite = func_suite()
    runner = NoofaRunner()
    runner.run(suite)
