import Pyro4

import ims.common.config as config


def start_name_server():
    cfg = config.get()
    Pyro4.naming.startNSloop(host=cfg.rpc.name_server_ip,
                             port=cfg.rpc.name_server_port)
