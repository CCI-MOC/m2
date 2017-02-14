import Pyro4

import ims.common.config as config
import ims.common.constants as constants


def start_name_server():
    cfg = config.get()
    port = int(cfg.rpc.name_server_port)
    Pyro4.naming.startNSloop(host=cfg.rpc.name_server_ip,
                             port=port)
