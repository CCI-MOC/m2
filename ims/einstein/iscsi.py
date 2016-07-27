import subprocess

import os

import ims.common.constants as constants
from ims.exception import *


class IET:
    def __init__(self, keyring, id, pool, password):
        self.keyring = keyring
        self.id = id
        self.pool = pool
        self.password = password

    def create_mapping(self, ceph_img_name):
        mappings = self.show_mappings()
        if ceph_img_name in mappings:
            raise iscsi_exceptions.NodeAlreadyInUseException()
        rbd_name = self.__execute_map(ceph_img_name)
        self.__add_mapping(ceph_img_name, rbd_name)
        self.__restart()

    def delete_mapping(self, ceph_img_name):
        iscsi_mappings = self.show_mappings()
        if ceph_img_name not in iscsi_mappings:
            raise iscsi_exceptions.NodeAlreadyUnmappedException()
        self.__stop()
        mappings = self.__execute_showmapped()
        self.__remove_mapping(ceph_img_name, mappings[ceph_img_name])
        self.__execute_unmap(mappings[ceph_img_name])
        self.__restart()

    def show_mappings(self):
        target_lines = []
        lun_lines = []
        with open(constants.IET_ISCSI_CONFIG_LOC, 'r') as fi:
            for line in fi:
                line = line.strip()
                if line.startswith(constants.IET_TARGET_STARTING):
                    target_lines.append(line)
                elif line.startswith(constants.IET_LUN_STARTING):
                    lun_lines.append(line)
        mappings = {}
        for i in xrange(target_lines.__len__()):
            target_line = target_lines[i]
            lun_line = lun_lines[i]
            mappings[target_line.split('.')[2]] = \
                lun_line.split(',')[0].split('=')[1]

        return mappings

    def __add_mapping(self, ceph_img_name, rbd_name):
        with open(constants.IET_ISCSI_CONFIG_LOC, 'a') as fi:
            fi.write(constants.IET_MAPPING_TEMP.replace(constants.CEPH_IMG_NAME,
                                                        ceph_img_name).replace(
                constants.RBD_NAME, rbd_name))

    def __remove_mapping(self, ceph_img_name, rbd_name):
        with open(constants.IET_ISCSI_CONFIG_LOC, 'r') as fi:
            with open(constants.IET_ISCSI_CONFIG_TEMP_LOC, 'w') as temp:
                for line in fi:
                    if line.find(ceph_img_name) == -1 and line.find(
                            rbd_name) == -1:
                        temp.write(line)
        os.rename(constants.IET_ISCSI_CONFIG_TEMP_LOC,
                  constants.IET_ISCSI_CONFIG_LOC)

    def __execute_map(self, ceph_img_name):
        command = "echo {0} | sudo -S rbd --keyring {1} --id {2} map {3}/{4}".format(
            self.password, self.keyring, self.id, self.pool, ceph_img_name)
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE)
        output, err = p.communicate()
        return output.strip()

    def __execute_unmap(self, rbd_name):
        command = "echo {0} | sudo -S rbd --keyring {1} --id {2} unmap {3}".format(
            self.password, self.keyring, self.id, rbd_name)
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE)
        output, err = p.communicate()

    def __execute_showmapped(self):
        p = subprocess.Popen('rbd showmapped', shell=True,
                             stdout=subprocess.PIPE)
        output, err = p.communicate()
        lines = output.split('\n')[1:-1]
        maps = {}
        for line in lines:
            parts = line.split()
            maps[parts[2]] = parts[4]
        return maps

    def __restart(self):
        command = "echo {0} | sudo -S service iscsitarget restart".format(
            self.password)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, err = p.communicate()

    def __stop(self):
        command = "echo {0} | sudo -S service iscsitarget stop".format(
            self.password)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, err = p.communicate()
