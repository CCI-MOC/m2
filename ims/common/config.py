import ConfigParser

import os

import ims.common.constants as constants
import ims.exception.config_exceptions as config_exceptions
from ims.common.bmi_config import parse_config

__config = None


def load(force=False):
    """
    Loads the config by using BMI_CONFIG environment variable, else loads from
    default location

    :param force: Forces a reload of config
    :return: None
    """
    global __config
    if __config is None or force:
        try:
            path = os.environ[
                constants.CONFIG_LOCATION_ENV_VARIABLE]
        except KeyError:
            path = constants.CONFIG_DEFAULT_LOCATION
        __config = BMIConfig(path)
        __config.load_config()
        parse_config(__config)


def get():
    """
    Returns the global config

    :return: The Global Config
    """
    global __config
    return __config


class BMIConfig:
    """ Contains the config of bmi as attributes """

    def __init__(self, filename):
        self.configfile = filename
        self.config = ConfigParser.SafeConfigParser()

    def load_config(self):
        """
        Loads the config as per the given path

        :return: None
        """
        if not self.config.read(self.configfile):
            raise IOError('cannot load ' + self.configfile)

    def option(self, section, option, type=str, required=True):
        """
        Parses the given option from config, converts to another type if
        required or raises an exception if found missing and adds it as
        attribute to config as cfg.section.option

        :param section: Section under which Option should be present
        :param option: Option should be parsed
        :param type: the conversion function for the required type like int,etc
        :param required: Whether an exception should be raised if missing
        :return: None
        """
        try:
            value = self.config.get(section, option)
            section_obj = getattr(self, section, None)
            if section_obj is None:
                section_obj = ConfigSection()
                setattr(self, section, section_obj)
            if type is bool:
                v = value.lower()
                if v in ['true', 'false']:
                    setattr(section_obj, option, v == 'true')
                else:
                    raise ValueError
            else:
                setattr(section_obj, option, type(value))
        except ConfigParser.Error:
            if required:
                raise config_exceptions.MissingOptionInConfigException(option,
                                                                       section)
        except ValueError:
            raise config_exceptions.InvalidValueConfigException(option,
                                                                section)

    def section(self, section_name, required=True):
        """
        Parses entire section and adds them to config object like option

        :param section_name: the section to parse
        :param required: Whether an exception should be raised if missing
        :return: None
        """
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
    """ A Simple Object to be used to get cfg.section.option """
    def __init__(self):
        pass
