from noofa.tests.base import NoofaSuite, NoofaRunner
from noofa.tests.components.dataschema import TestDataschema
from noofa.tests.components.components import TestComponentsSchema


def components_suite():
    suite = NoofaSuite()
    suite.add(TestDataschema)
    suite.add(TestComponentsSchema)
    return suite


def run_tests():
    suite = components_suite()
    runner = NoofaRunner()
    runner.run(suite)
