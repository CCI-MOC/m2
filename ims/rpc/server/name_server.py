import Pyro4

import ims.common.config as config
import ims.common.constants as constants


def start_name_server():
    cfg = config.get()
    Pyro4.naming.startNSloop(host=cfg.rpc[constants.RPC_NAME_SERVER_IP_KEY], port=int(cfg.rpc[constants.RPC_NAME_SERVER_PORT_KEY]))
