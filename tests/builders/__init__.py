from noofa.tests.base import NoofaSuite, NoofaRunner
from noofa.tests.builders.builder import TestBuilder


def builders_suite():
    suite = NoofaSuite()
    suite.add(TestBuilder)
    return suite


def run_tests():
    suite = builders_suite()
    runner = NoofaRunner()
    runner.run(suite)
