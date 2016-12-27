import ConfigParser
import os

import ims.common.constants as constants
from ims.exception import *

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

        self.fs_name = None
        self.iscsi_name = None
        self.netiso_name = None

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read(self.configfile):
                raise IOError('cannot load ' + self.configfile)

            # Should Raise Exception if two fs, netiso, iscsi are present
            # Clueless about previous comment
            for section in config.sections():
                if section.startswith(constants.FS_PREFIX_CONFIG_NAME):
                    self.fs_name = section[
                                   len(constants.FS_PREFIX_CONFIG_NAME) + 1:]
                    self.fs = dict(config.items(section))
                elif section.startswith(constants.NETISO_PREFIX_CONFIG_NAME):
                    self.netiso_name = section[
                            len(constants.NETISO_PREFIX_CONFIG_NAME) + 1:]
                    self.netiso = dict(config.items(section))
                elif section.startswith(constants.ISCSI_PREFIX_CONFIG_NAME):
                    self.iscsi_name = section[
                            len(constants.ISCSI_PREFIX_CONFIG_NAME) + 1:]
                    self.iscsi = dict(config.items(section))

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
