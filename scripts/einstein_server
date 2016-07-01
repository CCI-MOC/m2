#!/usr/bin/python

import multiprocessing

from ims.rpc.server.nameserver import *
from ims.rpc.server.rpcserver import *

import ims.common.config as config


config.load(constants.EINSTEIN_CONFIG_FLAG)

p1 = multiprocessing.Process(target=start_name_server)
p2 = multiprocessing.Process(target=start_rpc_server)

p1.start()
p2.start()

print "Nameserver Process ID = "+str(p1.pid)
print "RPC Server Process ID = "+str(p2.pid)

p1.join()
p2.join()
