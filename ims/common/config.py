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

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        if not config.read(self.configfile):
            raise IOError('cannot load ' + self.configfile)
        self.config = config

        # Mandatory Options
        self.__parse_option(constants.BMI_CONFIG_SECTION_NAME,
                            constants.UID_KEY)
        self.__parse_option(constants.BMI_CONFIG_SECTION_NAME,
                            constants.SERVICE_KEY)
        self.__parse_option(constants.DB_CONFIG_SECTION_NAME,
                            constants.DB_PATH_KEY)
        self.__parse_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_RPC_SERVER_IP_KEY)
        self.__parse_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_RPC_SERVER_PORT_KEY)
        self.__parse_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_NAME_SERVER_IP_KEY)
        self.__parse_option(constants.RPC_CONFIG_SECTION_NAME,
                            constants.RPC_NAME_SERVER_PORT_KEY)
        self.__parse_option(constants.TFTP_CONFIG_SECTION_NAME,
                            constants.PXELINUX_PATH_KEY)
        self.__parse_option(constants.TFTP_CONFIG_SECTION_NAME,
                            constants.IPXE_PATH_KEY)
        self.__parse_option(constants.REST_API_CONFIG_SECTION_NAME,
                            constants.REST_API_IP_KEY)
        self.__parse_option(constants.REST_API_CONFIG_SECTION_NAME,
                            constants.REST_API_PORT_KEY)
        self.__parse_option(constants.LOGS_CONFIG_SECTION_NAME,
                            constants.LOGS_PATH_KEY)
        self.__parse_option(constants.LOGS_CONFIG_SECTION_NAME,
                            constants.LOGS_DEBUG_KEY)
        self.__parse_option(constants.LOGS_CONFIG_SECTION_NAME,
                            constants.LOGS_VERBOSE_KEY)
        self.__parse_option(constants.FS_CONFIG_SECTION_NAME,
                            constants.DRIVER_KEY)
        self.__parse_option(constants.ISCSI_CONFIG_SECTION_NAME,
                            constants.DRIVER_KEY)
        self.__parse_option(constants.NET_ISOLATOR_CONFIG_SECTION_NAME,
                            constants.DRIVER_KEY)

        # Mandatory Sections (Typically Driver Sections)
        self.__parse_section(constants.ISCSI_CONFIG_SECTION_NAME)
        self.__parse_section(constants.NET_ISOLATOR_CONFIG_SECTION_NAME)
        self.__parse_section(constants.FS_CONFIG_SECTION_NAME)

        self.__parse_section(constants.TESTS_CONFIG_SECTION_NAME,
                             required=False)

    def __parse_option(self, section, option, required=True):
        try:
            value = self.config.get(section, option)
            section_obj = getattr(self, section, None)
            if section_obj is None:
                section_obj = ConfigSection()
                setattr(self, section, section_obj)
            setattr(section_obj, option, value)
        except ConfigParser.Error:
            if required:
                raise config_exceptions.MissingOptionInConfigException(option,
                                                                       section)

    def __parse_section(self, section_name, required=True):
        try:
            section = self.config.items(section_name)
            section_obj = getattr(self, section_name, None)
            if section_obj is None:
                section_obj = ConfigSection()
                setattr(self, section_name, section_obj)

            for name, value in section:
                setattr(section_obj, name, value)

        except ConfigParser.Error:
            if required:
                raise config_exceptions.MissingSectionInConfigException(
                    section_name)


class ConfigSection:
    def __init__(self):
        pass


if __name__ == "__main__":
    cfg = __BMIConfig("/home/sourabh/bmiconfig.cfg")
    cfg.parse_config()
    print dir(cfg)
    print dir(cfg.iscsi)
    print dir(cfg.fs)
    print dir(cfg.net_isolator)
