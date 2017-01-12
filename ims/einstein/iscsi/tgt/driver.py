import subprocess

import os
import re

import constants as tgt_constants
import ims.common.constants as constants
import ims.common.shell as shell
import ims.exception.config_exceptions as config_exceptions
import ims.exception.iscsi_exceptions as iscsi_exceptions
from ims.common.log import create_logger, log
from ims.interfaces.iscsi import ISCSI

logger = create_logger(__name__)


def get_driver_class():
    return TGT


class TGT(ISCSI):
    '''
        Class for implementing TGT
    '''

    def __init__(self, fs_config, iscsi_config):
        self.__validate(fs_config, iscsi_config)

    def __validate(self, fs_config, iscsi_config):
        section = None
        try:
            section = constants.FS_CONFIG_SECTION_NAME
            self.fs_config_loc = fs_config[tgt_constants.CEPH_CONFIG_FILE_KEY]
            self.fs_user = fs_config[tgt_constants.CEPH_ID_KEY]
            self.fs_pool = fs_config[tgt_constants.CEPH_POOL_KEY]

            section = constants.ISCSI_CONFIG_SECTION_NAME
            self.iscsi_ip = iscsi_config[tgt_constants.ISCSI_IP_KEY]
        except KeyError as e:
            raise config_exceptions.MissingOptionInConfigException(str(e),
                                                                   section)

    @property
    def ip(self):
        return self.iscsi_ip

    @log
    def start_server(self):
        '''
        Have to parse the output and send a status code.
        :return:
        '''
        try:
            output = shell.call(tgt_constants.START_COMMAND, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not tgt_constants.ACTIVE_STATUS:
                raise iscsi_exceptions.StartFailedException()
        except subprocess.CalledProcessError:
            raise iscsi_exceptions.StartFailedException()

    @log
    def stop_server(self):
        '''
        Need to check if this
        :return:
        '''
        try:
            output = shell.call(tgt_constants.STOP_COMMAND, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not tgt_constants.DEAD_STATE:
                raise iscsi_exceptions.StopFailedException()
        except subprocess.CalledProcessError:
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
        status_string = shell.call(tgt_constants.STATUS_COMMAND, sudo=True)
        logger.debug("Output = %s", status_string)
        if tgt_constants.ACTIVE_STATUS in status_string:
            return tgt_constants.ACTIVE_STATE
        elif tgt_constants.INACTIVE_STATUS in status_string:
            return tgt_constants.DEAD_STATE
        # Have to check if there are any other states
        else:
            return tgt_constants.ERROR_STATE

    def __generate_config_file(self, target_name):
        config = open(os.path.join(tgt_constants.TGT_ISCSI_CONFIG,
                                   target_name + ".conf"), 'w')
        template_loc = os.path.split(os.path.abspath(__file__))[0]
        for line in open(os.path.join(template_loc,
                                      tgt_constants.TEMPLATE_NAME), 'r'):
            line = line.replace(tgt_constants.TARGET_NAME, target_name)
            line = line.replace(tgt_constants.CEPH_USER, self.fs_user)
            line = line.replace(tgt_constants.CEPH_CONFIG, self.fs_config_loc)
            line = line.replace(tgt_constants.CEPH_POOL, self.fs_pool)
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
                output = shell.call(tgt_constants.TARGET_CREATION_COMMAND,
                                    sudo=True)
                logger.debug("Output = %s", output)
            else:
                raise iscsi_exceptions.TargetExistsException()
        except (IOError, OSError) as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))

    @log
    def remove_target(self, target_name):
        '''
        Removes target specified. Same as comment for above function.
        :return:
        '''
        try:
            targets = self.list_targets()
            if target_name in targets:
                os.remove(os.path.join(tgt_constants.TGT_ISCSI_CONFIG,
                                       target_name + ".conf"))
                command = tgt_constants.TARGET_DELETION_COMMAND.format(
                    target_name)
                output = shell.call(command, sudo=True)
                logger.debug("Output = %s", output)
            else:
                raise iscsi_exceptions.TargetDoesntExistException()
        except (IOError, OSError) as e:
            raise iscsi_exceptions.TargetDeletionFailed(str(e))
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.TargetDeletionFailed(str(e))

    @log
    def list_targets(self):
        '''
        Lists all the targets available. This queries tgt-admin and gets the
        list of targets
        :return:
        '''
        try:
            output = shell.call(tgt_constants.LIST_TARGETS_COMMAND, sudo=True)
            logger.debug("Output = %s", output)
            formatted_output = output.split("\n")
            target_list = [target.split(":")[1].strip() for target in
                           formatted_output if
                           re.match("^Target [0-9]+:", target)]
            return target_list
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.ListTargetFailedException(str(e))
