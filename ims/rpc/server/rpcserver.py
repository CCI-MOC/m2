import Pyro4

import ims.common.config as config
import ims.common.constants as constants
from ims.einstein.operations import BMI
from ims.exception import *


class MainServer:
    # This method takes in the commandline arguments from the client program.
    # First argument is always the name of the method that is to be run.
    # The commandline arguments following that are the arguments to the method.
    def execute_command(self, credentials, command, args):
        try:
            print "In Server"
            with BMI(credentials) as bmi:
                print "In with"
                method_to_call = getattr(BMI, command)
                args.insert(0, bmi)
                args = tuple(args)
                output = method_to_call(*args)
                return output
        except BMIException as ex:
            return ex


def start_rpc_server():
    cfg = config.get()
    Pyro4.config.HOST = cfg.rpcserver_ip
    # Starting the Pyro daemon, locating and registering object with name server.
    daemon = Pyro4.Daemon(port=cfg.rpcserver_port)
    # find the name server
    ns = Pyro4.locateNS(host=cfg.nameserver_ip, port=cfg.nameserver_port)
    # register the greeting maker as a Pyro object
    uri = daemon.register(MainServer)
    # register the object with a name in the name server
    ns.register(constants.RPC_SERVER_NAME, uri)
    print("Ready.")
    daemon.requestLoop()  # start the event loop of the server to wait for calls
