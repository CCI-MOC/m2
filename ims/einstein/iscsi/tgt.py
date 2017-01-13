import subprocess

import os
import re

import ims.exception.iscsi_exceptions as iscsi_exceptions
from ims.common.log import create_logger, log
from ims.interfaces.iscsi import ISCSI

logger = create_logger(__name__)


class TGT(ISCSI):
    '''
        Class for implementing TGT
    '''

    # We should get all the config related to ceph in here.
    # Also, root_password is something that can be avoided.

    # Also removed sudo everywhere since it was causing issues
    def __init__(self, fs_config_loc, fs_user, root_password):
        self.arglist = ["service", "tgtd"]
        self.TGT_ISCSI_CONFIG = "/etc/tgt/conf.d/"
        self.fs_config_loc = fs_config_loc
        self.fs_user = fs_user
        self.root_password = root_password

    @log
    def start_server(self):
        '''
        Have to parse the output and send a status code.
        :return:
        '''
        # arglist = self.arglist
        # arglist.append("start")
        # Need to fix shell=True everywhere
        command = "service tgtd start"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
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
        # arglist = self.arglist
        # arglist.append("stop")
        command = "service tgtd stop"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
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
        # arglist = self.arglist
        # arglist.append('status')
        command = "service tgtd status"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
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
        config = open(self.TGT_ISCSI_CONFIG + target_name + ".conf", 'w')
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         ".."))
        for line in open(template_loc + "/tgt_target.temp", 'r'):
            line = line.replace('${target_name}', target_name)
            line = line.replace('${ceph_user}', self.fs_user)
            line = line.replace('${ceph_config}', self.fs_config_loc)
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
                # tgtarglist = ["sudo", "-S", "tgt-admin", "--execute"]
                command = "tgt-admin --execute".format(self.root_password)
                proc = subprocess.Popen(command, shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                proc.communicate()
                if proc.returncode != 0:
                    raise iscsi_exceptions.UpdateConfigFailedException(
                        "Adding new target failed at creating target file \
                        stage")
            else:
                raise iscsi_exceptions.NodeAlreadyInUseException()
        except (IOError, OSError) as e:
            logger.info("Update config exception")
            raise iscsi_exceptions.UpdateConfigFailedException(str(e))
        except (iscsi_exceptions.MountException,
                iscsi_exceptions.DuplicatesException) as e:
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
                os.remove(self.TGT_ISCSI_CONFIG + target_name + ".conf")
                # tgtarglist = ["sudo", "-S","tgt-admin", "--execute"]
                command = "tgt-admin -f --delete {0}".format(target_name)
                proc = subprocess.Popen(command, shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                proc.communicate()
                if proc.returncode != 0:
                    raise iscsi_exceptions.UpdateConfigFailedException(
                        "Deleting target failed at deleting target file stage")
            else:
                raise iscsi_exceptions.NodeAlreadyUnmappedException()
                # The above should be something like NodeAlreadyDeleted
        except (IOError, OSError) as e:
            # For checking if we have access to directory for file
            # creation/deletion
            logger.info("Update config exception")
            raise iscsi_exceptions.UpdateConfigFailedException(e.message)
        except (iscsi_exceptions.MountException,
                iscsi_exceptions.DuplicatesException) as e:
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
        # arglist = ["sudo", "-S", "tgt-admin", "-s"]
        command = "tgt-admin -s".format(self.root_password)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        # output, err = proc.communicate(self.root_password+"\n")
        output, err = proc.communicate()
        logger.debug("Output = %s, Error = %s", output, err)
        if proc.returncode != 0:
            raise iscsi_exceptions.InvalidConfigException("Listing targets \
                                                          failed")
            # This exception has to be modified. I prefer writing a new
            # exception which is something like iscsi_communication exception
        else:
            formatted_output = output.split("\n")
            target_list = [target.split(":")[1].strip() for target in
                           formatted_output if
                           re.match("^Target [0-9]+:", target)]
            return target_list
