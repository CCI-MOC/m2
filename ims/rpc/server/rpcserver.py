import Pyro4
from ims.einstein.operations import *
import ims.common.config as config

class MainServer(object):
    def __init__(self,ip):
    #This is the ip address of the machine on which the host is binded on.
        Pyro4.config.HOST = ip
     #Takes in the list_of_commands passed by the client program.
    
    #This method takes in the commandline arguments from the client program.
    #First argument is always the name of the method that is to be run.
    #The commandline arguments following that are the arguments to the method.
    def run_script(self, credentials, list_of_commands):
        try:
            list_of_commands[0].decode('utf-8')
            print "in utf-8"


            bmi = BMI(credentials)
            methodToCall = getattr(BMI, list_of_commands[0])
            list_of_commands[0] = bmi
            args = tuple(list_of_commands)
            output = methodToCall(*args)
            return output
        except UnicodeError:
            print "Not utf-8"
        except Exception as e:
            import traceback
            traceback.print_exc(e)


def start_rpc_server():
    cfg = config.load()
    MainServer(cfg.rpcserver_ip)
    #Starting the Pyro daemon, locating and registering object with name server.
    daemon = Pyro4.Daemon(port=cfg.rpcserver_port)                # make a Pyro daemon
    ns = Pyro4.locateNS(host=cfg.nameserver_ip,port=cfg.nameserver_port)                  # find the name server
    uri = daemon.register(MainServer)   # register the greeting maker as a Pyro object
    ns.register("example.mainserver", uri)   # register the object with a name in the name server
    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls
