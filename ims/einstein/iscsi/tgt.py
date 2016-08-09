import io
import subprocess
import re
from ims.common.log import *
from ims.exception import *
from ims.interfaces.iscsi import *

logger = create_logger(__name__)


class TGT(ISCSI):
    '''
        Class for implementing TGT
    '''

    # We should get all the config related to ceph in here.
    # Also, root_password is something that can be avoided.
    def __init__(self, fs_config_loc, fs_user, root_password):
        self.arglist = ["sudo", "-S", "service", "tgtd"]
        self.TGT_ISCSI_CONFIG = "/etc/tgt/conf.d"
        self.fs_config_loc = fs_config_loc
        self.fs_user = fs_user
        self.root_password = root_password

    @log
    def start_server(self):
        '''
        Have to parse the output and send a status code.
        :return:
        '''
        arglist = self.arglist
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
        arglist = self.arglist 
        arglist = arglist.append("stop")
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate(self.root_password + "\n")
        logger.debug("Output = %s, Error = %s", output, err)
        if self.show_status() is not 'Dead':
            raise iscsi_exceptions.StopFailedException()
    
    @log
    def restart_server(self):
        '''
        Again have to parse the output and send the values.
        :return:
        '''
        self.stop_server()
        self.start_server()

    @log
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

    @log
    def add_target(self, target_name):
        '''
        Adds target
        :param target_name: Name of target to be added.
        :return:
        '''
        try:
            targets = self.list_targets()
            if target_name not in targets:
                self.__generate_config_file(target_name)
                tgtarglist = ["sudo", "-S", "tgt-admin", "--execute"]
                proc = subprocess.Popen(tgtarglist, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                proc.communicate(self.root_password + "\n")
                if proc.returncode != 0:
                    raise iscsi_exceptions.UpdateConfigFailedException("Adding
                    new target failed at creating target file stage")
            else:
                raise iscsi_exceptions.NodeAlreadyInUseException()
        except OSError as e:
            logger.info("Update config exception")
            raise iscsi_exceptions.UpdateConfigFailedException(e.message)
        except (iscsi_exceptions.MountException,
                iscsi_exceptions.DuplicateException) as e:
            logger.info("Error exposing iscsi_target")
            raise e
    
    @log
    def remove_target(self, target_name):
        '''
        Removes target specified. Same as comment for above function.
        :return:
        '''
        try:
            targets = self.list_targets()
            if target_name in targets:
                targetremoved = ["rm", self.TGT_ISCSI_CONFIG + target_name + ".conf"]
                subprocess.Popen(targetremoved, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()
                tgtarglist = ["sudo", "-S","tgt-admin", "--execute"]
                subprocess.Popen(tgtarglist, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()
                if proc.returncode != 0:
                    raise iscsi_exceptions.UpdateConfigFailedException("Deleting
                    target failed at deleting target file stage")
            else:
                raise iscsi_exceptions.NodeAlreadyUnmappedException()
                # The above should be something like NodeAlreadyDeleted
        except OSError as e:
            # For checking if we have access to directory for file
            # creation/deletion
            logger.info("Update config exception")
            raise iscsi_exceptions.UpdateConfigFailedException(e.message)
        except (iscsi_exceptions.MountException,
                iscsi_exceptions.DuplicateException) as e:
                # Do we still need the above exceptions? Duplicate
                # exception can be avoided by checking lists as shown above
                # Mouting is something that we are not doing now?
            logger.info("Error exposing iscsi_target")
            raise e               
    
    @log
    def list_targets(self):
        '''
        Lists all the targets available. This queries tgt-admin and gets the
        list of targets
        :return:
        '''
        arglist = ["sudo", "-S", "tgt-admin", "-s"]
        proc = subprocess.Popen(arglist,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = proc.communicate(self.root_password+"\n")
        logger.debug("Output = %s, Error = %s", output, err)
        if proc.returncode !=0:
            raise iscsi_exceptions.InvalidConfigException("Listing targets
            failed")
            # This exception has to be modified. I prefer writing a new
            # exception which is something like iscsi_communication exception
        else:
            formatted_output = output.split("\n")
            target_list = [target.split(":")[1].strip() for target in
            formatted_output if re.match("^Target [0-9]+:", target)]
            return target_list
       
