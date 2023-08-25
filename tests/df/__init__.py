from noofa.tests.base import NoofaSuite, NoofaRunner
from noofa.tests.df.panda_filters import TestPandaFilters
from noofa.tests.df.panda_builder import TestPandaBuilder


def df_suite():
    suite = NoofaSuite()
    suite.add(TestPandaFilters)
    suite.add(TestPandaBuilder)
    return suite


def run_tests():
    suite = df_suite()
    runner = NoofaRunner()
    runner.run(suite)
