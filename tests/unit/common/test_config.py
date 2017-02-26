import unittest

import os

import ims.common.config as config
import ims.exception.config_exceptions as config_exceptions
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
        os.environ['BMI_CONFIG'] = "tests/unit/common/config1.cfg"

    def runTest(self):
        config.load(force=True)
        cfg = config.get()
        self.assertEqual(cfg.tests.var1, '0')

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestMissingOption(unittest.TestCase):
    """ Tests If raising exception when option is missing """

    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/config2.cfg"

    def runTest(self):
        with self.assertRaises(
                config_exceptions.MissingOptionInConfigException):
            config.load(force=True)

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestMissingSection(unittest.TestCase):
    """ Tests if raising exception when section is missing """
    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/config3.cfg"

    def runTest(self):
        with self.assertRaises(
                config_exceptions.MissingSectionInConfigException):
            config.load(force=True)

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestInvalidValue(unittest.TestCase):
    """ Tests if raising exception when invalid value is given """
    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/config4.cfg"

    def runTest(self):
        with self.assertRaises(config_exceptions.InvalidValueConfigException):
            config.load(force=True)

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestInvalidBool(unittest.TestCase):
    """ Tests If raising exception when invalid bool is given """
    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/config5.cfg"

    def runTest(self):
        with self.assertRaises(config_exceptions.InvalidValueConfigException):
            config.load(force=True)

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestMissingOptionalSection(unittest.TestCase):
    """ Tests if loading when optional section is missing """
    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/config6.cfg"

    def runTest(self):
        config.load(force=True)
        cfg = config.get()
        self.assertIsNone(getattr(cfg, 'tests', None))

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)


class TestMissingOptionalOption(unittest.TestCase):
    """ Tests if loading when optional option is missing """
    @trace
    def setUp(self):
        self.old_path = os.getenv('BMI_CONFIG')
        os.environ['BMI_CONFIG'] = "tests/unit/common/config1.cfg"

    def runTest(self):
        config.load(force=True)
        cfg = config.get()
        cfg.option('bmi', 'sample', required=False)
        self.assertIsNone(getattr(cfg.bmi, 'sample', None))

    def tearDown(self):
        os.environ['BMI_CONFIG'] = self.old_path
        config.load(force=True)
