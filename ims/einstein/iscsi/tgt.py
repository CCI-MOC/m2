import subprocess

import os
import re

import ims.common.shell as shell
import ims.exception.iscsi_exceptions as iscsi_exceptions
from ims.common.log import create_logger, log
from ims.interfaces.iscsi import ISCSI

logger = create_logger(__name__)


class TGT(ISCSI):
    """ Class for implementing TGT """

    def __init__(self, fs_config_loc, fs_user, fs_pool):
        self.TGT_ISCSI_CONFIG = "/etc/tgt/conf.d/"
        self.fs_config_loc = fs_config_loc
        self.fs_user = fs_user
        self.fs_pool = fs_pool

    @log
    def start_server(self):
        """
        Starts the tgt service

        :return: None
        """
        try:
            command = "service tgtd start"
            output = shell.call(command, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not 'Running':
                raise iscsi_exceptions.StartFailedException()
        except subprocess.CalledProcessError:
            raise iscsi_exceptions.StartFailedException()

    @log
    def stop_server(self):
        """
        Stops the tgtd service

        :return: None
        """
        try:
            command = "service tgtd stop"
            output = shell.call(command, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not 'Dead':
                raise iscsi_exceptions.StopFailedException()
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.StopFailedException()

    @log
    def restart_server(self):
        """
        Restarts the tgtd service

        :return: None
        """
        self.stop_server()
        self.start_server()

    @log
    def show_status(self):
        """
        Returns the status of tgtd

        :return: Running or Dead or Error as String
        """
        command = "service tgtd status"
        status_string = shell.call(command, sudo=True)
        logger.debug("Output = %s", status_string)
        if 'active (running)' in status_string:
            return 'Running'
        elif 'inactive (dead)' in status_string:
            return 'Dead'
        # Have to check if there are any other states
        else:
            return "Error"

    def __generate_config_file(self, target_name):
        """
        Generates the config file in conf.d/

        :param target_name: Target for which config file should be created
        :return: None
        """
        config = open(
            os.path.join(self.TGT_ISCSI_CONFIG, target_name + ".conf"), 'w')
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         ".."))
        for line in open(os.path.join(template_loc, "tgt_target.temp"), 'r'):
            line = line.replace('${target_name}', target_name)
            line = line.replace('${ceph_user}', self.fs_user)
            line = line.replace('${ceph_config}', self.fs_config_loc)
            line = line.replace('${pool}', self.fs_pool)
            config.write(line)
        config.close()

    @log
    def add_target(self, target_name):
        """
        Adds target

        :param target_name: Name of target to be added
        :return: None
        """
        try:
            targets = self.list_targets()
            if target_name not in targets:
                self.__generate_config_file(target_name)
                command = "tgt-admin --execute"
                output = shell.call(command, sudo=True)
                logger.debug("Output = %s", output)
            else:
                raise iscsi_exceptions.TargetExistsException()
        except (IOError, OSError) as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))

    @log
    def remove_target(self, target_name):
        """
        Removes target specified

        :param target_name: Name of target to be removed
        :return: None
        """
        try:
            targets = self.list_targets()
            if target_name in targets:
                os.remove(os.path.join(self.TGT_ISCSI_CONFIG,
                                       target_name + ".conf"))
                command = "tgt-admin -f --delete {0}".format(target_name)
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
        """
        Lists all the targets available by querying tgt-admin

        :return: None
        """
        try:
            command = "tgt-admin -s"
            output = shell.call(command, sudo=True)
            logger.debug("Output = %s", output)
            formatted_output = output.split("\n")
            target_list = [target.split(":")[1].strip() for target in
                           formatted_output if
                           re.match("^Target [0-9]+:", target)]
            return target_list
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.ListTargetFailedException(str(e))
