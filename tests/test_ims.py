import unittest

import click
import re

import ims.common.config as config

config.load()


def get_test_cases(suite):
    """
    Returns a list of Test Cases that are part of the given Test Suite

    :param suite: The Test Suite whose Test Cases needs to be extracted
    :return: A List of Test Cases
    """
    test_cases = set()
    for test in suite:
        if not isinstance(test, unittest.TestSuite):
            test_cases.add(test)
        else:
            results = get_test_cases(test)
            test_cases = test_cases.union(results)
    return test_cases


def fetch_all_tests():
    """
    Loads and returns all test cases in the tests directory

    :return: A List of Test Cases
    """
    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    return get_test_cases(tests)


def get_class_name(cls):
    """
    Returns the fully qualified name of the class

    :param cls: the class whose name needs to be returned
    :return: Class Name as String
    """
    return str(cls)[8:-2]


def filter_tests(pattern, tests):
    """
    Returns a list of test cases that match the given pattern

    :param pattern: The regex pattern that needs to be matched
    :param tests: The list of test cases that needs to be filtered
    :return: A List of test cases
    """
    filtered_tests = set()
    for test in tests:
        if re.search(pattern, get_class_name(test.__class__)) is not None:
            filtered_tests.add(test)
    return filtered_tests


def run_tests(tests):
    """
    Runs the given tests

    :param tests: The List of Test Cases to run
    :return: None
    """
    suite = unittest.TestSuite(tests)
    test_runner = unittest.TextTestRunner(verbosity=3)
    test_runner.run(suite)


@click.group()
def cli():
    """
    The Testing Framework for BMI, do test_ims run --help for more details
    """


@cli.command(short_help="Runs the test cases as per the given patterns")
@click.argument('test_case_patterns', nargs=-1)
@click.option('-i', '--interactive', is_flag=True, help="Interactive Mode")
def run(test_case_patterns, interactive):
    """
    Runs the test cases as per the given patterns

    \b
    Arguments:
    TEST_CASE_PATTERNS = Any Number of Regex expressions for finding test cases
    """
    tests = fetch_all_tests()
    filtered_tests = set()
    for pattern in test_case_patterns:
        filtered_tests = filtered_tests.union(filter_tests(pattern, tests))

    if interactive:
        print "List of Loaded Test Cases\n"
        for test in filtered_tests:
            print get_class_name(test.__class__)
        print "\nCount of Test Cases Loaded = %s" % len(filtered_tests)
        response = raw_input("Do you want to run them ? (y/n) ").lower()
        if response in ['n', 'no']:
            return
    run_tests(filtered_tests)


if __name__ == "__main__":
    cli()
