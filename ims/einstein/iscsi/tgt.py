import os
import re

from ims.common import shell
from ims.common.log import create_logger, log
from ims.exception import iscsi_exceptions
from ims.exception import shell_exceptions
from ims.exception.exception import ShellException
from ims.interfaces.iscsi import ISCSI

from pssh.clients import ParallelSSHClient, SSHClient
from pssh.exceptions import UnknownHostException
from gevent import joinall

logger = create_logger(__name__)


class TGT(ISCSI):
    """ Class for implementing TGT """

    # TODO add TGT_ISCSI_CONFIG in config, update in PR related to Issue #30
    # TODO add service name in config
    def __init__(self, fs_config_loc, fs_user, fs_pool, tgt_template_file, primary_iscsi, secondary_iscsi=None):
        self.TGT_ISCSI_CONFIG = "/etc/tgt/conf.d/"
        self.fs_config_loc = fs_config_loc
        self.fs_user = fs_user
        self.fs_pool = fs_pool
        self.primary_iscsi = primary_iscsi
        self.secondary_iscsi = secondary_iscsi
        self.tgt_template_file = tgt_template_file
        if secondary_iscsi is None:
            self.client = SSHClient([primary_iscsi])
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
            output = self.client.run_command(command)
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.StartFailedException()
        
        for status in output.values():
            assert status.exit_code == 0, "Failed to start TGTd"

    @log
    def stop_server(self):
        """
        Stops the tgtd service on both iscsi servers.

        :return: None
        """
        try:
            command = 'sudo systemctl stop tgtd'
            output = self.client.run_command(command)
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.StopFailedException()
        
        for status in output.values():
            assert status.exit_code == 0, "Failed to stop TGTd"

    @log
    def restart_server(self):
        """
        Restarts the tgtd service

        :return: None
        """
        try:
            command = 'sudo systemctl restart tgtd'
            output = self.client.run_command(command)
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.RestartFailedException()
        
        for status in output.values():
            assert status.exit_code == 0, "Failed to restart TGTd"

    @log
    def assert_running(self):
        """
        Asserts that both iscsi servers are reachable
        and have tgtd running.  

        :return: None.
        """
        # Get the status of tgtd from both machines
        command = "systemctl is-active tgtd"
        try:
            output = self.client.run_command(command)
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.ListTargetFailedException(str(e))
        # Store the output in dictionaries
        for status in output.values():
            assert status.exit_code == 0, "TGT is not active on one of the servers"

    def __generate_config_file(self, target_name):
        """
        Generates the config file in conf.d/

        :param target_name: Target for which config file should be created
        :return: None
        """
        # Create the config file in /tmp/
        config_file_name = target_name + ".conf"
        config_file_path = os.path.join('/tmp/', config_file_name)
        try:
            config = open(config_file_path, 'w')
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
            cmds = self.client.copy_file(config_file_path, self.TGT_ISCSI_CONFIG + config_file_name)
            if self.secondary_iscsi is not None:
                joinall(cmds, raise_error=True)
                # Check pxssh errors here
        except UnknownHostException as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))

        # Delete the file from /tmp/
        os.remove(config_file_path)

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
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))
        
        for status in output.values():
            assert status.exit_code == 0, "Faied to add target on one or both machines"

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
        command = "sudo tgt-admin -f --delete {0}".format(target_name)
        try:
            # Delete the configuration file from both remote hosts
            delete_file = 'sudo rm -f ' + config_file
            self.client.run_command(delete_file)
            # Then delete the target
            output = self.client.run_command(command)
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.TargetDeletionFailed(str(e))
        
        for status in output.values():
            assert status.exit_code == 0, "Faied to add remove target form one or both machines"

    @log
    def list_targets(self):
        """
        Lists all the targets available by querying tgt-admin.
        
        We check both primary and secondary servers for the list.
        If the targets dont match no both hosts, an assertion error
        is raised.
        :return: target list
        """
        # Run the tgt command to collect the raw output
        command = "sudo tgt-admin -s|grep Target"
        try:
            output = self.client.run_command(command)
            self.client.join(output)
        except UnknownHostException as e:
            raise iscsi_exceptions.ListTargetFailedException(str(e))
        
        target = {}
        # Store targets from both iscsi servers
        for host, host_output in output.items():
            target[host] = []
            for line in host_output.stdout:
                target[host].append(line)
        logger.debug("Output = %s", target)

        # Make sure both iscsi servers have the same targets
        if self.secondary_iscsi is not None:
            assert target[self.primary_iscsi] == target[self.secondary_iscsi]

        # Prepare the target_list to be returned.
        target_list = [target.split(":")[1].strip() for target in
                       target[self.primary_iscsi] if
                       re.match("^Target [0-9]+:", target)]
        return target_list

