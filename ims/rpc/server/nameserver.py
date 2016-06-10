import Pyro4

import ims.common.config as config


def start_name_server():
    cfg = config.load()
    Pyro4.naming.startNSloop(host=cfg.nameserver_ip, port=cfg.nameserver_port)
