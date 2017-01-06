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
    """
        Class for implementing TGT
    """

    # We should get all the config related to ceph in here.
    # Also, root_password is something that can be avoided.

    # Also removed sudo everywhere since it was causing issues
    def __init__(self, fs_config, iscsi_config):
        self.ceph_config = fs_config[constants.CEPH_CONFIG_FILE_KEY]
        self.ceph_id = fs_config[constants.CEPH_ID_KEY]
        self.pool = fs_config[constants.CEPH_POOL_KEY]
        self.provision_net_ip = iscsi_config[tgt_constants.TGT_ISCSI_IP_KEY]
        self.root_password = iscsi_config[tgt_constants.TGT_ISCSI_PASSWORD_KEY]

    @property
    def ip(self):
        return self.provision_net_ip

    @log
    def start_server(self):
        """
        Have to parse the output and send a status code.
        :return:
        """
        output = ""
        with sh.sudo:
            output = sh.service.tgtd.start()
        logger.debug("Output = %s", output)

        if self.show_status() is 'Running':
            raise iscsi_exceptions.StartFailedException()

    @log
    def stop_server(self):
        """
        Need to check if this
        :return:
        """
        output = ""
        with sh.sudo:
            output = sh.service.tgtd.stop()
        logger.debug("Output = %s", output)
        if self.show_status() is not 'Dead':
            raise iscsi_exceptions.StopFailedException()

    @log
    def restart_server(self):
        """
        Again have to parse the output and send the values.
        :return:
        """
        self.stop_server()
        self.start_server()

    @log
    def show_status(self):
        status_string = ""
        with sh.sudo:
            status_string = sh.service.tgtd.status()
        logger.debug("Output = %s", status_string)
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
        """
        Adds target
        :param target_name: Name of target to be added.
        :return:
        """
        try:
            targets = self.list_targets()
            if target_name not in targets:
                self.__generate_config_file(target_name)
                tgt_admin = sh.Command(tgt_constants.TGT_ADMIN_PATH)
                output = ""
                with sh.sudo:
                    output = tgt_admin(execute=True)
                logger.debug("Output = %s", output)
            else:
                raise iscsi_exceptions.TargetExistsException()

        except sh.ErrorReturnCode as e:
            raise iscsi_exceptions.TargetCreationFailedException(str(e))
        except (IOError, OSError) as e:
            logger.info("Target Creation Failed Due to " + str(e))
            raise iscsi_exceptions.TargetCreationFailedException(str(e))

    @log
    def remove_target(self, target_name):
        """
        Removes target specified. Same as comment for above function.
        :return:
        """
        try:
            targets = self.list_targets()
            if target_name in targets:
                os.remove(
                    tgt_constants.TGT_ISCSI_CONFIG + target_name + ".conf")
                tgt_admin = sh.Command(tgt_constants.TGT_ADMIN_PATH)
                output = ""
                with sh.sudo:
                    output = tgt_admin(f=True, delete=target_name)
                logger.debug("Output = %s", output)
            else:
                raise iscsi_exceptions.TargetDoesntExistException()
                # The above should be something like NodeAlreadyDeleted
        except sh.ErrorReturnCode as e:
            raise iscsi_exceptions.TargetDeletionFailedException(str(e))
        except (IOError, OSError) as e:
            # For checking if we have access to directory for file
            # creation/deletion
            logger.info("Target Deletion Failed Due to " + str(e))
            raise iscsi_exceptions.TargetDeletionFailedException(str(e))

    @log
    def list_targets(self):
        """
        Lists all the targets available. This queries tgt-admin and gets the
        list of targets
        :return:
        """
        try:
            output = ""
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
            raise iscsi_exceptions.ListTargetFailedException(str(e))