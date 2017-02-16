import ConfigParser

import os

import ims.common.constants as constants
import ims.exception.config_exceptions as config_exceptions
from ims.common.bmi_config import parse_config

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
        __config.load_config()
        parse_config(__config)


def get():
    global __config
    return __config


class __BMIConfig:
    # other instance variables are initialized as to not get AttributeErrors
    def __init__(self, filename):
        self.configfile = filename
        self.config = None

    def load_config(self):
        config = ConfigParser.SafeConfigParser()
        if not config.read(self.configfile):
            raise IOError('cannot load ' + self.configfile)
        self.config = config

    def option(self, section, option, type=str, required=True):
        try:
            value = self.config.get(section, option)
            section_obj = getattr(self, section, None)
            if section_obj is None:
                section_obj = ConfigSection()
                setattr(self, section, section_obj)
            if type == bool:
                setattr(section_obj, option, value.lower() == 'true')
            else:
                setattr(section_obj, option, type(value))
        except ConfigParser.Error:
            if required:
                raise config_exceptions.MissingOptionInConfigException(option,
                                                                       section)

    def section(self, section_name, required=True):
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
