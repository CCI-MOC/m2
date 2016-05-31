import Pyro4


# from rpcserver_backup import *

class RPCClient(object):
    def __init__(self):
        # Loads the variable dict with the contents of config.json.
        self.dict = {
            "function-list": {
                "provision": "3",
                "detach_node": "1",
                "create_snapshot": "3",
                "list_all_images": "1",
                "list_snaps": "2",
                "remove_snaps": "3"
            }
        }
        self.func_list = self.dict[
            'function-list']  # The script name and no. of arguments.

    def concatenate_command(self, list_of_commands):
        concatenated_command = ""
        concatenated_command += " ".join(list_of_commands[1:])
        return concatenated_command

    def correct_argument_list_length(self, list_of_commands):
        return (
        len(list_of_commands) - 1 <= int(self.func_list[list_of_commands[0]]))

    # This method checks for escape characters or injection attacks.
    def escape_characters_present(self, concatenated_command):
        # The escape_chars set contains all the characters which if present would terminate the program
        # execution
        escape_chars = set(';<>&|\'')
        if any((c in escape_chars) for c in concatenated_command):
            return True
        else:
            return False

    # client_function(): This function does all the check required, calls the
    # server program with the method name and arguments passed in as a list
    # and prints the output received from the server.
    def client_function(self, main_obj, list_of_commands, debug=False):
        # print(main_obj)
        # print(self.func_list.has_key(list_of_commands[0]))
        print self.func_list
        if (self.func_list.has_key(list_of_commands[0])):
            print "after func list"
            concatenated_command = self.concatenate_command(list_of_commands)
            print concatenated_command
            if ((not self.escape_characters_present(
                    concatenated_command)) and self.correct_argument_list_length(
                    list_of_commands)):
                print "in concatenated"
                # print("Entering the object")
                # main_obj = MainServer()
                print list_of_commands
                return main_obj.run_script(list_of_commands)
        elif debug == True:
            print("Invalid argument.")


# if __name__ == "__main__":
def client_rpc(command):
    client = RPCClient()
    list_of_commands = command
    name_server = Pyro4.locateNS(host="192.168.122.34",
                                 port=9092)  # Locates the name server
    uri = name_server.lookup(
        "example.mainserver")  # Looks up for the registered service in the name server
    main_obj = Pyro4.Proxy(uri)
    print "Done"
    print client
    print main_obj
    print list_of_commands
    return client.client_function(main_obj, list_of_commands)
