import Pyro4
import sys

class RPCClient(object):
    def __init__(self):
        #Function list is created as an element under dict so that new 
        #elements could be added without touching the function-list.
        self.dict = {
                   "function-list" : {
                            "provision" : "4",
                            "detach_node" : "1",
                            "create_snapshot" : "2",
                            "list_all_images" : "1",
                            "list_snaps" : "1",
                            "remove_snaps" : "2"
                            },
                    "nameserver-address" : "192.168.122.34",
                    "nameserver-port" : 9090
                     } 
        self.func_list = self.dict['function-list'] #The script name and no. of arguments.
    
    def concatenate_command(self, list_of_commands):
        concatenated_command = ""
        concatenated_command += " ".join(list_of_commands[1:])
        return concatenated_command
   
    def correct_argument_list_length(self, list_of_commands):
        return (len(list_of_commands)-1 <= int(self.func_list[list_of_commands[0]]))

    #This method checks for escape characters or injection attacks.
    def escape_characters_present(self, concatenated_command):
    #The escape_chars set contains all the characters which if present would terminate the program
    #execution  
        escape_chars = set(';<>&|\'')
        if any((c in escape_chars) for c in concatenated_command):
            return True
        else:
            return False
    
    #client_function(): This function does all the check required, calls the 
    #server program with the method name and arguments passed in as a list
    #and prints the output received from the server.  
    def client_function(self, list_of_commands)
        if (self.func_list.has_key(list_of_commands[0])):
            concatenated_command = self.concatenate_command(list_of_commands)
            if((not self.escape_characters_present(concatenated_command)) \
                and self.correct_argument_list_length(list_of_commands)):
                print main_obj.run_script(list_of_commands)
            else:
                print("Invalid arguments.")
        else:
            print("Invalid argument.")

if __name__ == "__main__":
    client =  RPCClient()
    list_of_commands = sys.argv[1:]
    name_server = Pyro4.locateNS(host=client.dict['nameserver-address'],port=client.dict['nameserver-port']) #Locates the name server
    uri = name_server.lookup("example.mainserver") #Looks up for the registered service in the name server
    main_obj = Pyro4.Proxy(uri)
    client.client_function(list_of_commands)

