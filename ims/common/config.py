import ConfigParser

import constants
from ims.exception import *

__config = None


def load(filename='bmiconfig.cfg'):
    try:
        global __config
        if __config is None:
            __config = __BMIConfig(filename)
            __config.parse_config()
    except ConfigException as ex:
        raise


def get():
    global __config
    return __config


class __BMIConfig:
    # the config file is hardcoded for now
    # other instance variables are initialized as to not get AttributeErrors
    def __init__(self, filename):
        self.configfile = filename
        self.fs = {}
        self.iscsi_update = None
        self.iscsi_update_password = None
        self.haas_url = None
        self.nameserver_ip = None
        self.nameserver_port = None
        self.rpcserver_ip = None
        self.rpcserver_port = None

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

            self.nameserver_ip = config.get(constants.RPC_CONFIG_SECTION_NAME,
                                            constants.RPC_NAME_SERVER_IP_KEY)
            self.nameserver_port = int(
                config.get(constants.RPC_CONFIG_SECTION_NAME,
                           constants.RPC_NAME_SERVER_PORT_KEY))
            self.rpcserver_ip = config.get(constants.RPC_CONFIG_SECTION_NAME,
                                           constants.RPC_RPC_SERVER_IP_KEY)
            self.rpcserver_port = int(
                config.get(constants.RPC_CONFIG_SECTION_NAME,
                           constants.RPC_RPC_SERVER_PORT_KEY))

            for k, v in config.items(constants.FILESYSTEM_CONFIG_SECTION_NAME):
                if v == 'True':
                    self.fs[k] = {}

                    for key, value in config.items(k):
                        self.fs[k][key] = value
        # Didn't Test
        except ConfigParser.NoOptionError as e:
            raise config_exceptions.MissingOptionInConfigException(e.args[0])
