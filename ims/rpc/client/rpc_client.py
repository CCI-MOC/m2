import Pyro4

import ims.common.config as config
import ims.common.constants as constants


class RPCClient:
    def __init__(self):
        # Loads the variable dict with the contents of config.json.
        self.dict = {
            "function-list": {
                "provision": "5",
                "deprovision": "3",
                "create_snapshot": "2",
                "list_images": "0",
                "list_snapshots": "0",
                "remove_image": "1"
            }
        }
        # The script name and no. of arguments.
        self.func_list = self.dict['function-list']
        cfg = config.get()
        # Locates the name server
        name_server = Pyro4.locateNS(host=cfg.nameserver_ip,
                                     port=cfg.nameserver_port)
        # Looks up for the registered service in the name server
        uri = name_server.lookup(constants.RPC_SERVER_NAME)
        self.main_obj = Pyro4.Proxy(uri)

    def __correct_argument_list_length(self, command, args):
        return len(args) == int(self.func_list[command])

    # This method checks for escape characters or injection attacks.
    def __escape_characters_present(self, concatenated_command):
        escape_chars = set(';<>&|\'')
        if any((c in escape_chars) for c in concatenated_command):
            return True
        else:
            return False

    # client_function(): This function does all the check required, calls the
    # server program with the method name and arguments passed in as a list
    # and prints the output received from the server.
    def execute_command(self, command, credentials, args):
        if command in self.func_list:
            concatenated_command = command + (" ".join(args))
            if ((not self.__escape_characters_present(
                    concatenated_command)) and self.__correct_argument_list_length(
                command, args)):
                print "Before"
                execute_command = self.main_obj.execute_command(credentials,
                                                                command, args)
                print "After"
                return execute_command
