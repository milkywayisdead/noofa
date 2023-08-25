from noofa.tests.base import NoofaSuite, NoofaRunner
from noofa.tests.sources.conn import TestParseConnString
from noofa.tests.sources.query_build import (
    TestQueryComponents,
    TestQueryPreparation,
    TestQueryBuild,
    TestQueryFilters,
)


def sources_suite():
    suite = NoofaSuite()
    suite.add(TestParseConnString)
    suite.add(TestQueryComponents)
    suite.add(TestQueryPreparation)
    suite.add(TestQueryBuild)
    suite.add(TestQueryFilters)
    return suite


def run_tests():
    suite = sources_suite()
    runner = NoofaRunner()
    runner.run(suite)
