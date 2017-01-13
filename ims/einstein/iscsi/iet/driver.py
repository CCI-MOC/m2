import subprocess

import os

import constants as iet_constants
import ims.common.constants as constants
import ims.common.shell as shell
import ims.exception.config_exceptions as config_exceptions
import ims.exception.iscsi_exceptions as iscsi_exceptions
from ceph import RBD
from ims.common.log import create_logger, log
from ims.interfaces.iscsi import ISCSI

logger = create_logger(__name__)


# Not Tested so beware!!
class IET(ISCSI):
    @log
    def __init__(self, fs_config, iscsi_config):
        self.fs = RBD(fs_config)
        self.__validate(iscsi_config)

    def __validate(self, iscsi_config):
        try:
            self.iscsi_ip = iscsi_config[iet_constants.ISCSI_IP_KEY]
        except KeyError as e:
            section = constants.FS_CONFIG_SECTION_NAME
            raise config_exceptions.MissingOptionInConfigException(str(e),
                                                                   section)

    @property
    def ip(self):
        return self.iscsi_ip

    @log
    def add_target(self, ceph_img_name):
        rbd_name = None
        try:
            mappings = self.list_targets()
            if ceph_img_name in mappings:
                raise iscsi_exceptions.TargetExistsException()
            rbd_name = self.fs.map(ceph_img_name)
            self.__add_mapping(ceph_img_name, rbd_name)
            self.restart_server()
        except subprocess.CalledProcessError as e:
            raise iscsi_exceptions.TargetCreationFailed(str(e))
        except IOError as e:
            maps = self.fs.showmapped()
            self.fs.unmap(maps[ceph_img_name])
            raise iscsi_exceptions.TargetCreationFailed(str(e))
        except iscsi_exceptions.RestartFailedException as e:
            self.__remove_mapping(ceph_img_name, rbd_name)
            maps = self.fs.showmapped()
            self.fs.unmap(maps[ceph_img_name])
            raise iscsi_exceptions.TargetCreationFailed(str(e))

    @log
    def remove_target(self, ceph_img_name):
        mappings = None
        try:
            iscsi_mappings = self.list_targets()
            if ceph_img_name not in iscsi_mappings:
                raise iscsi_exceptions.TargetDoesntExistException()
            self.stop_server()
            mappings = self.fs.showmapped()
            self.__remove_mapping(ceph_img_name, mappings[ceph_img_name])
            self.fs.unmap(mappings[ceph_img_name])
            self.restart_server()
        except (IOError, OSError) as e:
            self.restart_server()
            raise iscsi_exceptions.TargetDeletionFailed(str(e))
        except subprocess.CalledProcessError as e:
            self.__add_mapping(ceph_img_name, mappings(ceph_img_name))
            self.restart_server()
            raise iscsi_exceptions.TargetDeletionFailed(str(e))
        except iscsi_exceptions.RestartFailedException as e:
            self.fs.map(ceph_img_name)
            self.__add_mapping(ceph_img_name, mappings(ceph_img_name))
            self.restart_server()  # Kind of weird that trying to restart again
            raise iscsi_exceptions.TargetDeletionFailed(str(e))

    @log
    def list_targets(self):
        mappings = {}
        try:
            with open(iet_constants.IET_ISCSI_CONFIG_LOC, 'r') as fi:
                target = None
                for line in fi:
                    line = line.strip()
                    if line.startswith(iet_constants.IET_TARGET_STARTING):
                        if target is None:
                            target = line.split(' ')[1]
                        else:
                            raise iscsi_exceptions.ListTargetFailedException(
                                "Invalid Targets File")
                    elif line.startswith(iet_constants.IET_LUN_STARTING):
                        if target is not None:
                            mappings[target] = line.split(',')[0].split('=')[1]
                            target = None
                        else:
                            raise iscsi_exceptions.ListTargetFailedException(
                                "Invalid Targets File")

            return mappings
        except IOError as e:
            logger.info("List Targets Failed")
            raise iscsi_exceptions.ListTargetFailedException(str(e))

    @log
    def __add_mapping(self, ceph_img_name, rbd_name):
        template_line = iet_constants.IET_MAPPING_TEMP
        with open(iet_constants.IET_ISCSI_CONFIG_LOC, 'a') as fi:
            template_line = template_line.replace(iet_constants.CEPH_IMG_NAME,
                                                  ceph_img_name)
            template_line = template_line.replace(iet_constants.RBD_NAME,
                                                  rbd_name)
            fi.write(template_line)

    @log
    def __remove_mapping(self, ceph_img_name, rbd_name):
        with open(iet_constants.IET_ISCSI_CONFIG_LOC, 'r') as fi:
            with open(iet_constants.IET_ISCSI_CONFIG_TEMP_LOC, 'w') as temp:
                for line in fi:
                    if line.find(ceph_img_name) == -1 and line.find(
                            rbd_name) == -1:
                        temp.write(line)
        os.rename(iet_constants.IET_ISCSI_CONFIG_TEMP_LOC,
                  iet_constants.IET_ISCSI_CONFIG_LOC)

    @log
    def restart_server(self):
        try:
            output = shell.call(iet_constants.RESTART_COMMAND, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not iet_constants.ACTIVE_STATUS:
                raise iscsi_exceptions.RestartFailedException()
        except subprocess.CalledProcessError as e:
            logger.info("Raising Restart Failed Exception")
            raise iscsi_exceptions.RestartFailedException()

    @log
    def stop_server(self):
        try:
            output = shell.call(iet_constants.STOP_COMMAND, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not iet_constants.DEAD_STATE:
                raise iscsi_exceptions.StopFailedException()
        except subprocess.CalledProcessError as e:
            logger.info("Raising Stop Failed Exception")
            raise iscsi_exceptions.StopFailedException()

    def start_server(self):
        try:
            output = shell.call(iet_constants.START_COMMAND, sudo=True)
            logger.debug("Output = %s", output)
            if self.show_status() is not iet_constants.ACTIVE_STATUS:
                raise iscsi_exceptions.StartFailedException()
        except subprocess.CalledProcessError as e:
            logger.info("Raising Start Failed Exception")
            raise iscsi_exceptions.StartFailedException()

    def show_status(self):
        status_string = shell.call(iet_constants.STATUS_COMMAND, sudo=True)
        logger.debug("Output = %s", status_string)
        if iet_constants.ACTIVE_STATUS in status_string:
            return iet_constants.ACTIVE_STATE
        elif iet_constants.INACTIVE_STATUS in status_string:
            return iet_constants.DEAD_STATE
        # Have to check if there are any other states
        else:
            return iet_constants.ERROR_STATE

    def persist_targets(self):

        if not self.fs.showmapped():
            return

        mappings = self.list_targets()

        for k, v in mappings.items():
            self.__remove_mapping(k, v)

        for k, v in mappings.items():
            rbd_name = self.fs.map(k)
            self.__add_mapping(k, rbd_name)

        self.restart_server()
