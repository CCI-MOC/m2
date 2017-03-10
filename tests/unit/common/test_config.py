import unittest

import os

from ims.common import config

config.load()
from ims.exception import config_exceptions
from ims.common.log import trace


class TestBadPath(unittest.TestCase):
    """ Tests whether an exception is raised when loading from invalid path """

    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "blahblah.cfg"

    def runTest(self):
        with self.assertRaises(IOError):
            config.load(force=True)

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestCorrectPath(unittest.TestCase):
    """ Tests if able to load from correct path """

    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/sample.cfg"

    def runTest(self):
        config.load(force=True)
        cfg = config.get()
        self.assertEqual(cfg.tests.var1, '0')

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestForceFalse(unittest.TestCase):
    """ Tests if load with force false is working"""

    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/sample.cfg"
        config.load(force=True)

    def runTest(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load()
        cfg = config.get()
        self.assertEqual(cfg.tests.var1, '0')

    def tearDown(self):
        config.load(force=True)


class TestMissingOption(unittest.TestCase):
    """ Tests If raising exception when option is missing """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")
        self.cfg.config.add_section("test")

    def runTest(self):
        with self.assertRaises(
                config_exceptions.MissingOptionInConfigException):
            self.cfg.option("test", "var1")


class TestMissingSection(unittest.TestCase):
    """ Tests if raising exception when section is missing """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")

    def runTest(self):
        with self.assertRaises(
                config_exceptions.MissingSectionInConfigException):
            self.cfg.section('test')


class TestInvalidValue(unittest.TestCase):
    """ Tests if raising exception when invalid value is given """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")
        self.cfg.config.add_section('test')
        self.cfg.config.set('test', 'var1', 'hello')

    def runTest(self):
        with self.assertRaises(config_exceptions.InvalidValueConfigException):
            self.cfg.option('test', 'var1', type=int)


class TestInvalidBool(unittest.TestCase):
    """ Tests If raising exception when invalid bool is given """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")
        self.cfg.config.add_section('test')
        self.cfg.config.set('test', 'var1', 'hello')

    def runTest(self):
        with self.assertRaises(config_exceptions.InvalidValueConfigException):
            self.cfg.option('test', 'var1', type=bool)


class TestMissingOptionalSection(unittest.TestCase):
    """ Tests loading a config which has a missing optional section """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")

    def runTest(self):
        self.cfg.section('test', required=False)
        self.assertIsNone(getattr(self.cfg, 'test', None))


class TestMissingOptionalOption(unittest.TestCase):
    """ Tests loading a config which has a missing optional option """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")
        self.cfg.config.add_section('test')
        self.cfg.config.set('test', 'var1', 'hello')

    def runTest(self):
        self.cfg.option('test', 'var1')
        self.cfg.option('test', 'var2', required=False)
        self.assertIsNone(getattr(self.cfg.test, 'var2', None))
