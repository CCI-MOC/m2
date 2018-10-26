import os
import re

from ims.common import shell
from ims.common.log import create_logger, log
from ims.exception import iscsi_exceptions
from ims.exception import shell_exceptions
from ims.exception.exception import ShellException
from ims.interfaces.iscsi import ISCSI

from pssh.clients import ParallelSSHClient
from pssh.exceptions import UnknownHostException

logger = create_logger(__name__)


class TGT(ISCSI):
    """ Class for implementing TGT """

    # TODO add TGT_ISCSI_CONFIG in config, update in PR related to Issue #30
    # TODO add service name in config
    def __init__(self, fs_config_loc, fs_user, fs_pool, primary_iscsi, secondary_iscsi, tgt_template_file):
        self.TGT_ISCSI_CONFIG = "/etc/tgt/conf.d/"
        self.fs_config_loc = fs_config_loc
        self.fs_user = fs_user
        self.fs_pool = fs_pool
        if secondary_iscsi is None:
            self.client = ParallelSSHClient([primary_iscsi])
        else:
            self.client = ParallelSSHClient([primary_iscsi, secondary_iscsi])

    @log
    def start_server(self):
        """
        Starts the tgt service

        :return: None
        """
        try:
            command = 'sudo systemctl start tgtd'
            self.client.run_command(command)
        except UnknownHostException as e:
            raise iscsi_exceptions.StartFailedException()

    @log
    def stop_server(self):
        """
        Stops the tgtd service on both iscsi servers.

        :return: None
        """
        try:
            command = 'sudo systemctl stop tgtd'
            self.client.run_command(command)
        except UnknownHostException as e:
            raise iscsi_exceptions.StopFailedException()

    @log
    def restart_server(self):
        """
        Restarts the tgtd service

        :return: None
        """
        try:
            command = 'sudo systemctl restart tgtd'
            self.client.run_command(command)
        except UnknownHostException as e:
            raise iscsi_exceptions.RestartFailedException()

    @log
    def show_status(self):
        """
        Returns the status of tgtd

        :return: Running or Dead or Error as String
        """
        pass
        # FIXME: Actually check the status of TGTD on both machine
        # If TGTD is not running on any of the machine, raise an error.
        # Also, actually call this method in operations.py before doing
        # any other operation.

    def __generate_config_file(self, target_name):
        """
        Generates the config file in conf.d/

        :param target_name: Target for which config file should be created
        :return: None
        """
        # Create the config file in /tmp/
        try:
            config_file = os.path.join('/tmp/', target_name + ".conf")
            config = open(config_file, 'w')
            for line in open(self.tgt_template_file, 'r'):
                line = line.replace('${target_name}', target_name)
                line = line.replace('${ceph_user}', self.fs_user)
                line = line.replace('${ceph_config}', self.fs_config_loc)
                line = line.replace('${pool}', self.fs_pool)
                config.write(line)
            config.close()
        except (IOError, OSError) as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))

        # Copy the config file to the iscsi servers
        try:
            self.client.copy_file(config_file, self.TGT_ISCSI_CONFIG)
        except UnknownHostException as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))

        # Delete the file from /tmp/
        os.remove(config_file)

    # TODO Add tgt-admin to config
    @log
    def add_target(self, target_name):
        """
        Adds target

        :param target_name: Name of target to be added
        :return: None
        """
        targets = self.list_targets()
        if target_name in targets:
            raise iscsi_exceptions.TargetExistsException()

        self.__generate_config_file(target_name)
        command = "sudo tgt-admin --execute"
        try:
            output = self.client.run_command(command)
        except UnknownHostException as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))

    @log
    def remove_target(self, target_name):
        """
        Removes target specified

        :param target_name: Name of target to be removed
        :return: None
        """
        targets = self.list_targets()
        if target_name not in targets:
            raise iscsi_exceptions.TargetDoesntExistException()

        config_file = os.path.join(self.TGT_ISCSI_CONFIG, target_name + ".conf")
        command = "tgt-admin -f --delete {0}".format(target_name)
        try:
            # Delete the configuration file from both remote hosts
            delete_file = 'sudo rm -f ' + config_file
            self.client.run_command(delete_file)
            # Then delete the target
            output = self.client.run_command(command)
            logger.debug("Output = %s", output)
        except UnknownHostException as e:
            raise iscsi_exceptions.TargetDeletionFailed(str(e))

    @log
    def list_targets(self):
        """
        Lists all the targets available by querying tgt-admin.
        We only check the primary TGT server to get the list of targets.

        :return: target list
        """
        primary_client = ParallelSSHClient([primary_iscsi])
        command = "sudo tgt-admin -s"
        try:
            output = primary_client.run_command(command)
        except UnknownHostException as e:
            raise iscsi_exceptions.ListTargetFailedException(str(e))

        # The output returned by parallelSSHClient is a generator
        # so I am collecting all the lines in a list.
        # TODO: Test the consume output flag
        formatted_output = []
        for line in output.items()[0][1].stdout:
            formatted_output.append(line)
        logger.debug("Output = %s", formatted_output)

        target_list = [target.split(":")[1].strip() for target in
                       formatted_output if
                       re.match("^Target [0-9]+:", target)]
        return target_list
