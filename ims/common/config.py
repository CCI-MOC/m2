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
        self.fs = {}
        self.uid = None
        self.db_url = None
        self.iscsi_update_password = None
        self.iscsi_ip = None
        self.haas_url = None
        self.nameserver_ip = None
        self.nameserver_port = None
        self.rpcserver_ip = None
        self.rpcserver_port = None
        self.bind_ip = None
        self.bind_port = None
        self.logs_url = None
        self.logs_debug = None
        self.logs_verbose = None
        self.pxelinux_loc = None
        self.ipxe_loc = None

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read(self.configfile):
                raise IOError('cannot load ' + self.configfile)

            self.uid = config.get(constants.BMI_CONFIG_SECTION_NAME,
                                  constants.UID_KEY)

            self.is_service = config.get(constants.BMI_CONFIG_SECTION_NAME,
                                         constants.SERVICE_KEY) == 'True'

            self.db_url = config.get(constants.DB_CONFIG_SECTION_NAME,
                                     constants.DB_URL_KEY)

            self.iscsi_update_password = config.get(
                constants.ISCSI_CONFIG_SECTION_NAME,
                constants.ISCSI_PASSWORD_KEY)

            self.iscsi_ip = config.get(constants.ISCSI_CONFIG_SECTION_NAME,
                                       constants.ISCSI_IP_KEY)

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

            self.bind_ip = config.get(constants.HTTP_CONFIG_SECTION_NAME,
                                      constants.BIND_IP_KEY)
            self.bind_port = config.get(constants.HTTP_CONFIG_SECTION_NAME,
                                        constants.BIND_PORT_KEY)

            self.logs_url = config.get(constants.LOGS_CONFIG_SECTION_NAME,
                                       constants.LOGS_URL_KEY)
            self.logs_debug = config.get(constants.LOGS_CONFIG_SECTION_NAME,
                                         constants.LOGS_DEBUG_KEY) == 'True'
            self.logs_verbose = config.get(constants.LOGS_CONFIG_SECTION_NAME,
                                           constants.LOGS_VERBOSE_KEY) == 'True'
            self.pxelinux_loc = config.get(constants.TFTP_CONFIG_SECTION_NAME,
                                           constants.PXELINUX_URL_KEY)
            self.ipxe_loc = config.get(constants.TFTP_CONFIG_SECTION_NAME,
                                       constants.IPXE_URL_KEY)

            for k, v in config.items(constants.FILESYSTEM_CONFIG_SECTION_NAME):
                if v == 'True':
                    self.fs[k] = {}

                    for key, value in config.items(k):
                        self.fs[k][key] = value
        # Didn't Test
        except ConfigParser.NoOptionError as e:
            raise config_exceptions.MissingOptionInConfigException(e.args[0])
