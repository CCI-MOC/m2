import Pyro4
import Pyro4.errors

import ims.common.config as config
import ims.common.constants as constants
from ims.common.log import create_logger, log, trace

logger = create_logger(__name__)


class RPCClient:
    @log
    def __init__(self):
        # Loads the variable dict with the contents of config.json.
        self.dict = {
            "function-list": {
                "provision": "4",
                "deprovision": "3",
                "create_snapshot": "2",
                "list_images": "0",
                "list_snapshots": "0",
                "remove_image": "1"
            }
        }
        # The script name and no. of arguments.
        self.func_list = self.dict['function-list']
        self.cfg = config.get()
        self.name_server = None
        self.main_obj = None
        self.__get_main_obj()

    def __get_main_obj(self):
        try:
            # Locates the name server
            ns_ip = self.cfg.rpc.name_server_ip
            ns_port = self.cfg.rpc.name_server_port
            self.name_server = Pyro4.locateNS(host=ns_ip,
                                              port=ns_port)
            # Looks up for the registered service in the name server
            uri = self.name_server.lookup(constants.RPC_SERVER_NAME)
            self.main_obj = Pyro4.Proxy(uri)
        except Pyro4.errors.NamingError as e:
            return {constants.STATUS_CODE_KEY: 500,
                    constants.MESSAGE_KEY: str(e)}

    @trace
    def __correct_argument_list_length(self, command, args):
        return len(args) == int(self.func_list[command])

    # This method checks for escape characters or injection attacks.
    @trace
    def __escape_characters_present(self, concatenated_command):
        escape_chars = set(';<>&|\'')
        if any((c in escape_chars) for c in concatenated_command):
            return True
        else:
            return False

    # client_function(): This function does all the check required, calls the
    # server program with the method name and arguments passed in as a list
    # and prints the output received from the server.
    @log
    def execute_command(self, command, credentials, args):
        if command in self.func_list:
            concatenated_command = command + (" ".join(args))
            if ((not self.__escape_characters_present(
                    concatenated_command)) and
                    self.__correct_argument_list_length(command, args)):
                if self.main_obj is None:
                    output = self.__get_main_obj()
                    if output is not None:
                        return output

                try:
                    execute_command = self.main_obj.execute_command(
                        credentials,
                        command,
                        args)
                    return execute_command
                except Pyro4.errors.CommunicationError as e:
                    self.main_obj = None
                    return {constants.STATUS_CODE_KEY: 500,
                            constants.MESSAGE_KEY: str(e)}
