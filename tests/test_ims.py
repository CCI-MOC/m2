import imp
import unittest

import os

import ims.common.config as config

config.load()


def find_test_modules(skip_list):
    dir_name, cur_name = os.path.split(__file__)
    name_of_this_module, cur_ext = os.path.splitext(cur_name)
    modules = []
    for dirname, dirnames, filenames in os.walk(dir_name):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext == '.py' and name != '__init__' \
                    and name != name_of_this_module \
                    and name not in skip_list:
                path = os.path.join(dirname, filename)
                modules.append(imp.load_source(name, path))
    return modules


skip_list = []

modules = find_test_modules(skip_list)

loader = unittest.TestLoader()
tests = unittest.TestSuite()
for mod in modules:
    tests.addTest(loader.loadTestsFromModule(mod))

if __name__ == "__main__":
    testRunner = unittest.TextTestRunner()
    testRunner.run(tests)
    print tests.countTestCases()
