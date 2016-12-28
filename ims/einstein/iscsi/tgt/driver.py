import subprocess

import os
import re
import sh

import constants as tgt_constants
import ims.common.constants as constants
from ims.common.log import log, create_logger
from ims.exception import iscsi_exceptions
from ims.interfaces.iscsi import ISCSI

logger = create_logger(__name__)


def get_driver_class():
    return TGT


# Need to disable sudo tty for to work currently
class TGT(ISCSI):
    '''
        Class for implementing TGT
    '''

    # We should get all the config related to ceph in here.
    # Also, root_password is something that can be avoided.

    # Also removed sudo everywhere since it was causing issues
    def __init__(self, fs_config, iscsi_config):

        self.ceph_config = fs_config[constants.CEPH_CONFIG_FILE_KEY]
        self.ceph_id = fs_config[constants.CEPH_ID_KEY]
        self.pool = fs_config[constants.CEPH_POOL_KEY]
        self.provision_net_ip = iscsi_config[tgt_constants.ISCSI_IP_KEY]
        self.root_password = iscsi_config[tgt_constants.ISCSI_PASSWORD_KEY]

    @property
    def ip(self):
        return self.provision_net_ip

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
        config = open(tgt_constants.TGT_ISCSI_CONFIG + target_name + ".conf",
                      'w')
        template_loc = os.path.split(os.path.abspath(__file__))[0]
        for line in open(
                os.path.join(template_loc, tgt_constants.TGT_TEMP_NAME), 'r'):
            line = line.replace(tgt_constants.TGT_POOL_NAME, self.pool)
            line = line.replace(tgt_constants.TGT_TARGET_NAME, target_name)
            line = line.replace(tgt_constants.TGT_CEPH_ID, self.ceph_id)
            line = line.replace(tgt_constants.TGT_CEPH_CONFIG, self.ceph_config)
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
                # command = "tgt-admin --execute"
                # proc = subprocess.Popen(command, shell=True,
                #                         stdout=subprocess.PIPE,
                #                         stderr=subprocess.PIPE)
                # proc.communicate()
                # if proc.returncode != 0:
                #     raise iscsi_exceptions.UpdateConfigFailedException(
                #         "Adding new target failed at creating target file \
                #         stage")
                tgt_admin = sh.Command(tgt_constants.TGT_ADMIN_PATH)
                with sh.sudo:
                    tgt_admin(execute=True)
            else:
                raise iscsi_exceptions.NodeAlreadyInUseException()

        except sh.ErrorReturnCode as e:
            print str(e)
            raise iscsi_exceptions.UpdateConfigFailedException(
                "Adding new target failed at creating target file stage")
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
                os.remove(
                    tgt_constants.TGT_ISCSI_CONFIG + target_name + ".conf")
                # tgtarglist = ["sudo", "-S","tgt-admin", "--execute"]
                # command = "tgt-admin -f --delete {0}".format(target_name)
                # proc = subprocess.Popen(command, shell=True,
                #                         stdout=subprocess.PIPE,
                #                         stderr=subprocess.PIPE)
                # proc.communicate()
                # if proc.returncode != 0:
                #     raise iscsi_exceptions.UpdateConfigFailedException(
                #         "Deleting target failed at deleting target file stage")
                tgt_admin = sh.Command(tgt_constants.TGT_ADMIN_PATH)
                with sh.sudo:
                    tgt_admin(f=True, delete=target_name)
            else:
                raise iscsi_exceptions.NodeAlreadyUnmappedException()
                # The above should be something like NodeAlreadyDeleted
        except sh.ErrorReturnCode as e:
            raise iscsi_exceptions.UpdateConfigFailedException(
                "Deleting target failed at deleting target file stage")
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
        # command = "tgt-admin -s"
        # proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        #                         stderr=subprocess.PIPE)
        # # output, err = proc.communicate(self.root_password+"\n")
        # output, err = proc.communicate()
        try:
            output = "Nothing"
            tgt_admin = sh.Command(tgt_constants.TGT_ADMIN_PATH)
            with sh.sudo:
                output = tgt_admin(s=True)
            logger.debug("Output = %s", output)
            formatted_output = output.split("\n")
            target_list = [target.split(":")[1].strip() for target in
                           formatted_output if
                           re.match("^Target [0-9]+:", target)]
            return target_list
        except sh.ErrorReturnCode as e:
            raise iscsi_exceptions.InvalidConfigException("Listing targets \
                                                                      failed")
            # This exception has to be modified. I prefer writing a new
            # exception which is something like iscsi_communication exception
