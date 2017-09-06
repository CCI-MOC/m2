import Pyro4

import ims.common.config as config
import ims.common.constants as constants
from ims.common.log import create_logger, log
from ims.einstein.operations import BMI
from ims.exception.exception import BMIException

logger = create_logger(__name__)


class MainServer:
    # This method takes in the commandline arguments from the client program.
    # First argument is always the name of the method that is to be run.
    # The commandline arguments following that are the arguments to the method.
    @log
    def execute_command(self, credentials, command, args):
        """
        Executes the given BMI command

        :param credentials: The credentials that BMI will use to authenticate.
        :param command: The BMI command to execute
        :param args: The Arguments which should be given to BMI Command
        :return: a dict as { HTTP status code, Output or Error Message }
        """
        try:
            with BMI(credentials) as bmi:
                method_to_call = getattr(BMI, command)
                args.insert(0, bmi)
                args = tuple(args)
                output = method_to_call(*args)
                return output
        except BMIException as ex:
            logger.exception('')
            return {constants.STATUS_CODE_KEY: ex.status_code,
                    constants.MESSAGE_KEY: str(ex)}
        except Exception as ex:
            logger.exception('')
            return {constants.STATUS_CODE_KEY: 500,
                    constants.MESSAGE_KEY: str(ex)}

    @log
    def remake_mappings(self):
        try:
            with BMI("", "", constants.BMI_ADMIN_PROJECT) as bmi:
                bmi.remake_mappings()
        except:
            logger.exception('')


@log
def start_rpc_server():
    cfg = config.get()
    if cfg.bmi.service:
        server = MainServer()
        server.remake_mappings()
    Pyro4.config.HOST = cfg.rpc.rpc_server_ip
    # Starting the Pyro daemon, locating and registering object with name
    # server
    daemon = Pyro4.Daemon(port=cfg.rpc.rpc_server_port)
    # find the name server
    ns = Pyro4.locateNS(host=cfg.rpc.name_server_ip,
                        port=cfg.rpc.name_server_port)
    # register the greeting maker as a Pyro object
    uri = daemon.register(MainServer)
    # register the object with a name in the name server
    ns.register(constants.RPC_SERVER_NAME, uri)
    # start the event loop of the server to wait for calls
    daemon.requestLoop()
