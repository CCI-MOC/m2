import threading

from ims.rpc.server.nameserver import *
from ims.rpc.server.rpcserver import *

import ims.common.config as config


config.load()

t1 = threading.Thread(target=start_name_server)
t2 = threading.Thread(target=start_rpc_server)

t1.start()
t2.start()
