import ConfigParser

import constants
from exception import *


class BMIConfig:
    # the config file is hardcoded for now
    # other instance variables are initialized as to not get AttributeErrors
    def __init__(self):
        self.configfile = 'bmiconfig.cfg'
        self.fs = {}
        self.iscsi_update = None
        self.iscsi_update_password = None
        self.haas_url = None

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read(self.configfile):
                raise IOError('cannot load ' + self.configfile)

            self.iscsi_update = config.get(constants.ISCSI_CONFIG_SECTION_NAME,
                                           constants.ISCSI_URL_KEY)

            self.iscsi_update_password = config.get(
                constants.ISCSI_CONFIG_SECTION_NAME,
                constants.ISCSI_PASSWORD_KEY)

            self.haas_url = config.get(constants.HAAS_CONFIG_SECTION_NAME,
                                       constants.HAAS_URL_KEY)

            for k, v in config.items(constants.FILESYSTEM_CONFIG_SECTION_NAME):
                if v == 'True':
                    self.fs[k] = {}

                    for key, value in config.items(k):
                        self.fs[k][key] = value
        # Didn't Test
        except ConfigParser.NoOptionError as e:
            raise config_exceptions.MissingOptionInConfigException(e.args[0])
