#!/usr/bin/python
import base64
import subprocess
import time

import ims.common.config as config
from ims.database import *
from ims.einstein.ceph_wrapper import *
from ims.einstein.haas_wrapper import *
from ims.exception import *


# logging will be submitted later

class BMI:
    def __init__(self, credentials):
        self.__process_credentials(credentials)
        self.config = config.get()
        self.haas = HaaS(base_url=self.config.haas_url, usr=self.username,
                         passwd=self.password)

    def __does_project_exist(self):
        pr = ProjectRepository()
        pid = pr.fetch_id_with_name(self.project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            raise db_exceptions.ProjectNotFoundException(self.project)

        self.pid = pid

    def __get_image_id(self, name):
        imgr = ImageRepository()
        img_id = imgr.fetch_id_with_name_from_project(name, self.project)
        if img_id is None:
            raise db_exceptions.ImageNotFoundException(name)
        return str(img_id)

    def __process_credentials(self, credentials):
        base64_str, self.project = credentials
        self.__does_project_exist()
        self.username, self.password = tuple(
            base64.b64decode(base64_str).split(':'))

    # Calling shell script which executes a iscsi update as we don't have
    # rbd map in documentation.
    @staticmethod
    def __call_shellscript(*args):
        arglist = list(args)
        print arglist
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return proc.communicate()

    # A custom function which is wrapper around only success code that
    # we are creating.
    @staticmethod
    def __return_success(obj):
        return {constants.STATUS_CODE_KEY: 200, constants.RETURN_VALUE_KEY: obj}

    # Parses the Exception and returns the dict that should be returned to user
    @staticmethod
    def return_error(ex):

        # Replaces the image name with id in error string
        def swap_id_with_name(err_str):
            parts = err_str.split(" ")
            imgr = ImageRepository()
            name = imgr.fetch_name_with_id(parts[0].strip())
            if name is not None:
                parts[0] = name
            return " ".join(parts)

        if FileSystemException in ex.__class__.__bases__:
            return {constants.STATUS_CODE_KEY: ex.status_code,
                    constants.MESSAGE_KEY: swap_id_with_name(str(ex))}
        return {constants.STATUS_CODE_KEY: ex.status_code,
                constants.MESSAGE_KEY: str(ex)}

    # Provisions from HaaS and Boots the given node with given image
    def provision(self, node_name, img_name, snap_name, network, channel, nic):
        try:
            print "provision"
            self.haas.attach_node_to_project_network(node_name, network,
                                                     channel, nic)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                imgr = ImageRepository()
                imgr.insert(node_name, self.pid)
                img_id = imgr.fetch_id_with_name_from_project(node_name,
                                                              self.project)
                fs.clone(img_name.encode('utf-8'), snap_name.encode('utf-8'),
                         str(img_id).encode("utf-8"))
                ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
                # Should be changed to python script
                iscsi_output = BMI.__call_shellscript(self.config.iscsi_update,
                                                      ceph_config[
                                                          constants.CEPH_KEY_RING_KEY],
                                                      ceph_config[
                                                          constants.CEPH_ID_KEY],
                                                      ceph_config[
                                                          constants.CEPH_POOL_KEY],
                                                      str(img_id),
                                                      constants.ISCSI_CREATE_COMMAND,
                                                      self.config.iscsi_update_password)
                if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                    return BMI.__return_success(True)
                elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                    # Was not able to test this exception in test cases as the haas
                    # call was blocking this exception
                    # But it was raised during preparation of tests
                    # Rare exception
                    raise iscsi_exceptions.NodeAlreadyInUseException()
        except ISCSIException as e:
            imgr = ImageRepository()
            img_id = imgr.fetch_id_with_name_from_project(node_name,
                                                          self.project)
            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                fs.remove(img_id)
            imgr.delete_with_name_from_project(node_name, self.project)
            time.sleep(20)
            self.haas.detach_node_from_project_network(node_name, network, nic)
            return BMI.return_error(e)
        except FileSystemException as e:
            imgr = ImageRepository()
            imgr.delete_with_name_from_project(node_name, self.project)
            time.sleep(20)
            self.haas.detach_node_from_project_network(node_name, network, nic)
            return BMI.return_error(e)
        except DBException as e:
            time.sleep(20)
            self.haas.detach_node_from_project_network(node_name, network, nic)
            return BMI.return_error(e)
        except HaaSException as e:
            return BMI.return_error(e)

    # This is for detach a node and removing it from iscsi
    # and destroying its image
    def detach_node(self, node_name, network, nic):
        try:
            print "detach"
            self.haas.detach_node_from_project_network(node_name,
                                                       network, nic)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                img_id = self.__get_image_id(node_name)
                ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]

                iscsi_output = BMI.__call_shellscript(self.config.iscsi_update,
                                                      ceph_config[
                                                          constants.CEPH_KEY_RING_KEY],
                                                      ceph_config[
                                                          constants.CEPH_ID_KEY],
                                                      ceph_config[
                                                          constants.CEPH_POOL_KEY],
                                                      str(img_id),
                                                      constants.ISCSI_DELETE_COMMAND,
                                                      self.config.iscsi_update_password)
                if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                    imgr = ImageRepository()
                    imgr.delete_with_name_from_project(node_name, self.project)
                    ret = fs.remove(str(img_id).encode("utf-8"))
                    return BMI.__return_success(ret)
                elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                    raise iscsi_exceptions.NodeAlreadyUnmappedException()
        except (
        HaaSException, ISCSIException, FileSystemException, DBException) as e:
            return BMI.return_error(e)

    # Creates snapshot for the given image with snap_name as given name
    # fs_obj will be populated by decorator
    def create_snapshot(self, img_name, snap_name):
        try:
            self.haas.validate_project(self.project)
            img_id = self.__get_image_id(img_name)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                return BMI.__return_success(fs.snap_image(img_id, str(snap_name)))

        except (HaaSException, DBException, FileSystemException) as e:
            return BMI.return_error(e)

    # Lists snapshot for the given image img_name
    # URL's have to be read from BMI config file
    # fs_obj will be populated by decorator
    def list_snaps(self, img_name):
        try:
            self.haas.validate_project(self.project)
            img_id = self.__get_image_id(img_name)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                return BMI.__return_success(fs.list_snapshots(img_id))

        except (HaaSException, DBException, FileSystemException) as e:
            return BMI.return_error(e)

    # Removes snapshot snap_name for the given image img_name
    # fs_obj will be populated by decorator
    def remove_snaps(self, img_name, snap_name):
        try:
            self.haas.validate_project(self.project)
            img_id = self.__get_image_id(img_name)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                return BMI.__return_success(
                    fs.remove_snapshots(img_id, str(snap_name)))

        except (HaaSException, DBException, FileSystemException) as e:
            return BMI.return_error(e)

    # Lists the images for the project which includes the snapshot
    def list_all_images(self):
        try:
            self.haas.validate_project(self.project)
            imgr = ImageRepository()
            return BMI.__return_success(
                imgr.fetch_names_from_project(self.project))
        except (HaaSException, DBException) as e:
            return BMI.return_error(e)
