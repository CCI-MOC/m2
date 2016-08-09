import io
import subprocess

from ims.common.log import *
from ims.exception import *
from ims.interfaces.iscsi import *

logger = create_logger(__name__)


class TGT(ISCSI):
    '''
        Class for implementing TGT
    '''

    arglist = ["sudo", "-S", "service", "tgtd"]
    TGT_ISCSI_CONFIG = "/etc/tgt/conf.d"

    # We should get all the config related to ceph in here.
    # Also, root_password is something that can be avoided.
    def __init__(self, fs_config_loc, fs_user, root_password):
        self.fs_config_loc = fs_config_loc
        self.fs_user = fs_user
        self.root_password = root_password

    @log
    def start_server(self):
        '''
        Have to parse the output and send a status code.
        :return:
        '''
        arglist = TGT.arglist
        arglist.append("start")
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate(self.root_password +
                                       "\n")
        logger.debug("Output = %s, Error = %s", output, err)
        if self.show_status() is 'Running':
            raise iscsi_exceptions.StartFailedException()

    @log
    def stop_server(self):
        '''
        Need to check if this
        :return:
        '''
        arglist = self.arglist.append("stop") # Got to modify in places like this
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate(self.root_password + "\n")
        logger.debug("Output = %s, Error = %s", output, err)
        if self.show_status() is not 'Dead':
            raise iscsi_exceptions.StopFailedException()

    def restart_server(self):
        '''
        Again have to parse the output and send the values.
        :return:
        '''
        self.stop_server()
        self.start_server()

    def show_status(self):
        arglist = self.arglist.append("status")
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        status_string = proc.communicate(self.root_password + "\n")[0]
        if 'active (running)' in status_string:
            return 'Running'
        elif 'inactive (dead)' in status_string:
            return 'Dead'
        # Have to check if there are any other states
        else:
            return "Running in error state"

    def __generate_config_file(self, target_name):
        config = io.open(self.TGT_ISCSI_CONFIG + target_name + ".conf", 'w')
        for line in io.open("tgt_target.temp", 'r'):
            line = line.replace('${target_name}', target_name) # Didnt change all
            config.write(line)
        config.close()

    def add_target(self, target_name):
        '''
        Adds target. Again I am catching generic exception.
        This should be changed to catch specific exceptions
        :param target_name: Name of target to be added.
        :return:
        '''
        targets = self.list_targets()
        if target_name not in targets:
            self.__generate_config_file(target_name)
            tgtarglist = ["sudo", "-S", "tgt-admin", "--execute"]
            proc = subprocess.Popen(tgtarglist, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            proc.communicate(self.root_password + "\n")

            # Have to modify this to check for subprocess output and
            # return something based on it.

    def remove_target(self, target_name):
        '''
        Removes target specified. Same as comment for above function.
        :return:
        '''
        try:
            targetremoved = ["rm", self.TGT_ISCSI_CONFIG, target_name + ".conf"]
            subprocess.Popen(targetremoved, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()
            tgtarglist = ["tgt-admin", "--execute"]
            subprocess.Popen(tgtarglist, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()
            return "Successful"
        except Exception as e: # Remove this
            print e.message
            return "Error"

    def list_targets(self):
        '''
        Lists all the targets available. As of now, not filtering for
        directories but it should be taken care of later.
        :return:
        '''
        try:
            return [x.rstrip(".conf") for x in os.listdir(TGT.TGT_ISCSI_CONFIG)
                    if
                    x.endswith(".conf")]
        except Exception as e:
            print e.message
