import Pyro4
from ims.operations import *
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
        print '\n###hello script'
        print list_of_commands
        try:
            list_of_commands[0].decode('utf-8')
            print "in utf-8"
        except UnicodeError:
            print "Not utf-8"
        bmi = BMI('haasadmin',"admin1234")
        methodToCall = getattr(BMI, list_of_commands[0])
        print methodToCall
        list_of_commands[0] = bmi
        args = tuple(list_of_commands)
        try:
            output = methodToCall(*args)
            print "output = "+str(output)
            return output
        except Exception as e:
            import traceback
            traceback.print_exc(e)

if __name__ == "__main__":
    MainServer()
    #Starting the Pyro daemon, locating and registering object with name server.
    daemon = Pyro4.Daemon(port=10001)                # make a Pyro daemon
    ns = Pyro4.locateNS(host="192.168.122.34",port=9092)                  # find the name server
    uri = daemon.register(MainServer)   # register the greeting maker as a Pyro object
    ns.register("example.mainserver", uri)   # register the object with a name in the name server
    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls
