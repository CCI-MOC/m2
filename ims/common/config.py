import ConfigParser

import os

import ims.common.constants as constants
import ims.exception.config_exceptions as config_exceptions
from ims.exception.exception import ConfigException

__config = None


def load():
    try:
        global __config
        if __config is None:
            try:
                path = os.environ[
                    constants.CONFIG_LOCATION_ENV_VARIABLE]
            except KeyError:
                path = constants.CONFIG_DEFAULT_LOCATION
            __config = __BMIConfig(path)
            __config.parse_config()
    except ConfigException as ex:
        raise


def get():
    global __config
    return __config


class __BMIConfig:
    # other instance variables are initialized as to not get AttributeErrors
    def __init__(self, filename):
        self.configfile = filename
        self.bmi = {}
        self.fs = {}
        self.db = {}
        self.logs = {}
        self.rpc = {}
        self.http = {}
        self.iscsi = {}
        self.tftp = {}
        self.netiso = {}
        self.tests = {}

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read(self.configfile):
                raise IOError('cannot load ' + self.configfile)

            self.fs = dict(config.items(constants.FS_CONFIG_SECTION_NAME))
            self.netiso = dict(
                config.items(constants.NETISO_CONFIG_SECTION_NAME))
            self.iscsi = dict(config.items(constants.ISCSI_CONFIG_SECTION_NAME))
            self.tftp = dict(config.items(constants.TFTP_CONFIG_SECTION_NAME))
            self.bmi = dict(config.items(constants.BMI_CONFIG_SECTION_NAME))
            self.logs = dict(config.items(constants.LOGS_CONFIG_SECTION_NAME))
            self.http = dict(config.items(constants.HTTP_CONFIG_SECTION_NAME))
            self.rpc = dict(config.items(constants.RPC_CONFIG_SECTION_NAME))
            self.db = dict(config.items(constants.DB_CONFIG_SECTION_NAME))

            if constants.TESTS_CONFIG_SECTION_NAME in config.sections():
                self.tests = dict(
                    config.items(constants.TESTS_CONFIG_SECTION_NAME))

        # Didn't Test
        except ConfigParser.NoOptionError as e:
            raise config_exceptions.MissingOptionInConfigException(e.args[0])

    def __check_for_drivers(self):
        if constants.DRIVER_KEY not in self.fs:
            raise config_exceptions.DriverKeyNotFoundException(
                constants.FS_CONFIG_SECTION_NAME)
        if constants.DRIVER_KEY not in self.netiso:
            raise config_exceptions.DriverKeyNotFoundException(
                constants.NETISO_CONFIG_SECTION_NAME)
        if constants.DRIVER_KEY not in self.iscsi:
            raise config_exceptions.DriverKeyNotFoundException(
                constants.ISCSI_CONFIG_SECTION_NAME)
