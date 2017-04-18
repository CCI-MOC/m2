import os
import unittest

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
    """ Tests whether config from correct path is being loaded properly """

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


class TestBadConfigs(unittest.TestCase):
    """ Contains Tests for testing various invalid configs """

    @trace
    def setUp(self):
        self.cfg = config.BMIConfig("")
        self.cfg.config.add_section("test")
        self.cfg.config.set("test", "var1", "hello")

    def test_missing_option(self):
        """ Tests If raising exception when option is missing """
        with self.assertRaises(
                config_exceptions.MissingOptionInConfigException):
            self.cfg.option("test", "missing")

    def test_missing_section(self):
        """ Tests if raising exception when section is missing """
        with self.assertRaises(
                config_exceptions.MissingSectionInConfigException):
            self.cfg.section('test1')

    def test_invalid_value(self):
        """ Tests if raising exception when invalid value is given """
        with self.assertRaises(config_exceptions.InvalidValueConfigException):
            self.cfg.option('test', 'var1', type=int)

    def test_invalid_bool(self):
        """ Tests If raising exception when invalid bool is given """
        with self.assertRaises(config_exceptions.InvalidValueConfigException):
            self.cfg.option('test', 'var1', type=bool)

    def test_missing_optional_section(self):
        """ Tests loading a config which has a missing optional section """
        self.cfg.section('missing', required=False)
        self.assertIsNone(getattr(self.cfg, 'test', None))

    def test_missing_optional_option(self):
        """ Tests loading a config which has a missing optional option """
        self.cfg.option('test', 'var1')
        self.cfg.option('test', 'var2', required=False)
        self.assertIsNone(getattr(self.cfg.test, 'var2', None))
