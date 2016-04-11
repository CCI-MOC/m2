import Pyro4
import operations
import sys

class MainServer(object):
    def __init__(self):
    #This is the ip address of the machine on which the host is binded on.
        Pyro4.config.HOST = '192.168.122.34'
    #Takes in the list_of_commands passed by the client program.
    
    #This method takes in the commandline arguments from the client program.
    #First argument is always the name of the method that is to be run.
    #The commandline arguments following that are the arguments to the method.
    def run_script(self, list_of_commands):
        methodToCall = getattr(operations, list_of_commands[0])
        args = tuple(list_of_commands[1:]) 
        output = methodToCall(*args)
        return output

if __name__ == "__main__":
    MainServer()
    #Starting the Pyro daemon, locating and registering object with name server.
    daemon = Pyro4.Daemon()                # make a Pyro daemon
    ns = Pyro4.locateNS()                  # find the name server
    uri = daemon.register(MainServer)   # register the greeting maker as a Pyro object
    ns.register("example.mainserver", uri)   # register the object with a name in the name server
    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls
