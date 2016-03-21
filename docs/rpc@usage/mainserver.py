# saved as greeting-server.py
import Pyro4
import subprocess #Needed to run a shell command or script from python
import shlex #Used when a shell command is to be splitted into sections. Like below.
import json
import unittest

class MainServer(object):
    def __init__(self):
	#Loads the variable dict with the contents of config.json.
	self.dict = json.loads(open('config.json').read())
	self.server_details = self.dict['server-details'] #The server ip addresses.
	self.script_list = self.dict['script-list'] #The script name and no. of arguments.
	#This is the ip address of the machine on which the host is binded on.
	Pyro4.config.HOST = self.server_details['server-address']

    #Takes in the list_of_commands passed to the the Server program and concatentes everything 
    #into a single string
    def concatenate_command(self, list_of_commands):
	concatenated_command = self.script_list[list_of_commands[0]]['name'] + " "
        concatenated_command += " ".join(list_of_commands[1:])
	return concatenated_command
    
    #Splits the concatenated_command and returns a list of all the space separated commands in the
    def split_command(self, concatenated_command):
	return shlex.split(concatenated_command)
    
    #Takes in the concatenated_command, splits it and checks whether the number of argument
    #is same as that of required by the program.
    def correct_argument_list_length(self, concatenated_command, file_key_in_dict):
	list_m = self.split_command(concatenated_command)
        return (len(list_m)-1 == int(self.script_list[file_key_in_dict]['arguments']))
    
    #This method checks for escape characters or injection attacks.
    def escape_characters_present(self, concatenated_command):
	#The escape_chars set contains all the characters which if present would terminate the program
	#execution	
	escape_chars = set(';<>&:|\'')
	if any((c in escape_chars) for c in concatenated_command):
		return True
	else:
		return False

    #Takes in the list_of_commands passed by the client program.
    def run_script(self, list_of_commands):
        #concatenated_command contains a string with all the arguments passed to the client program
	concatenated_command = self.concatenate_command(list_of_commands)
	if ((not self.escape_characters_present(concatenated_command)) and self.correct_argument_list_length(concatenated_command, list_of_commands[0])):
		p = subprocess.Popen(shlex.split(concatenated_command), stdout=subprocess.PIPE)
        	(output, error) =  p.communicate()
        	return output
	else:
		return "The argument list passed is not acceptable. Please check the arguments you passed."				


if __name__ == "__main__":
	MainServer()
	#Starting the Pyro daemon, locating and registering object with name server.
	daemon = Pyro4.Daemon()                # make a Pyro daemon
	ns = Pyro4.locateNS()                  # find the name server
	uri = daemon.register(MainServer)   # register the greeting maker as a Pyro object
	ns.register("example.mainserver", uri)   # register the object with a name in the name server
	print("Ready.")
	daemon.requestLoop()                   # start the event loop of the server to wait for calls
