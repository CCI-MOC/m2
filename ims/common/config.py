import ConfigParser

import os

import ims.common.constants as constants
import ims.exception.config_exceptions as config_exceptions

__config = None


def load():
    global __config
    if __config is None:
        try:
            path = os.environ[
                constants.CONFIG_LOCATION_ENV_VARIABLE]
        except KeyError:
            path = constants.CONFIG_DEFAULT_LOCATION
        __config = __BMIConfig(path)
        __config.parse_config()


def get():
    global __config
    return __config


class __BMIConfig:
    # other instance variables are initialized as to not get AttributeErrors
    def __init__(self, filename):
        self.configfile = filename
        self.config = None
        # Mandatory Sections
        self.bmi = {}
        self.db = {}
        self.rpc = {}
        self.http = {}
        self.tftp = {}
        self.logs = {}

        # Driver Sections (Still Mandatory)
        self.fs = {}
        self.iscsi = {}
        self.net_isolator = {}

        # Optional Section
        self.tests = {}

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        if not config.read(self.configfile):
            raise IOError('cannot load ' + self.configfile)
        self.config = config

        # Mandatory Options
        self.__check_option(constants.BMI_CONFIG_SECTION_NAME,
                            constants.UID_KEY)
        self.__check_option(constants.BMI_CONFIG_SECTION_NAME,
                            constants.SERVICE_KEY)
        self.__check_option(constants.DB_CONFIG_SECTION_NAME,
                            constants.DB_PATH_KEY)
        self.__check_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_RPC_SERVER_IP_KEY)
        self.__check_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_RPC_SERVER_PORT_KEY)
        self.__check_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_NAME_SERVER_IP_KEY)
        self.__check_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_NAME_SERVER_PORT_KEY)
        self.__check_option(constants.TFTP_CONFIG_SECTION_NAME,
                            constants.PXELINUX_PATH_KEY)
        self.__check_option(constants.TFTP_CONFIG_SECTION_NAME,
                            constants.IPXE_PATH_KEY)
        self.__check_option(constants.HTTP_CONFIG_SECTION_NAME,
                            constants.BIND_IP_KEY)
        self.__check_option(constants.HTTP_CONFIG_SECTION_NAME,
                            constants.BIND_PORT_KEY)
        self.__check_option(constants.LOGS_CONFIG_SECTION_NAME,
                            constants.LOGS_PATH_KEY)
        self.__check_option(constants.LOGS_CONFIG_SECTION_NAME,
                            constants.LOGS_DEBUG_KEY)
        self.__check_option(constants.LOGS_CONFIG_SECTION_NAME,
                            constants.LOGS_VERBOSE_KEY)

        # Mandatory Sections (Typically Driver Sections)
        self.__check_option(constants.FS_CONFIG_SECTION_NAME,
                            constants.DRIVER_KEY)
        self.__check_option(constants.ISCSI_CONFIG_SECTION_NAME,
                            constants.DRIVER_KEY)
        self.__check_option(constants.NET_ISOLATOR_CONFIG_SECTION_NAME,
                            constants.DRIVER_KEY)

        self.fs = dict(config.items(constants.FS_CONFIG_SECTION_NAME))
        self.net_isolator = dict(
            config.items(constants.NET_ISOLATOR_CONFIG_SECTION_NAME))
        self.bmi = dict(config.items(constants.BMI_CONFIG_SECTION_NAME))
        self.db = dict(config.items(constants.DB_CONFIG_SECTION_NAME))
        self.logs = dict(config.items(constants.LOGS_CONFIG_SECTION_NAME))
        self.rpc = dict(config.items(constants.RPC_CONFIG_SECTION_NAME))
        self.http = dict(config.items(constants.HTTP_CONFIG_SECTION_NAME))
        self.iscsi = dict(config.items(constants.ISCSI_CONFIG_SECTION_NAME))
        self.tftp = dict(config.items(constants.TFTP_CONFIG_SECTION_NAME))

        # Optional Section for Testing Purposes
        if config.has_section(constants.TESTS_CONFIG_SECTION_NAME):
            self.tests = dict(
                config.items(constants.TESTS_CONFIG_SECTION_NAME))

    def __check_option(self, section, option):
        self.__check_section(section)
        if not self.config.has_option(section, option):
            raise config_exceptions.MissingOptionInConfigException(option,
                                                                   section)

    def __check_section(self, section):
        if not self.config.has_section(section):
            raise config_exceptions.MissingSectionInConfigException(
                section)
