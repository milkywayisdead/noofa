from noofa.tests.base import NoofaSuite, NoofaRunner
from noofa.tests.sources import sources_suite
from noofa.tests.df import df_suite
from noofa.tests.func import func_suite
from noofa.tests.components import components_suite
from noofa.tests.builders import builders_suite


def run_tests():
    suite = NoofaSuite()
    suite.add(sources_suite())
    suite.add(df_suite())
    suite.add(func_suite())
    suite.add(components_suite())
    suite.add(builders_suite())
    runner = NoofaRunner()
    runner.run(suite)


if __name__ == '__main__':
    run_tests()

