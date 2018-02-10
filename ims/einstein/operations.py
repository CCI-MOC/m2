#!/usr/bin/python
import base64
import time

import os

import ims.common.config as config
import ims.common.constants as constants
import ims.exception.db_exceptions as db_exceptions
from ims.common.log import create_logger, log, trace
from ims.database.database import Database
from ims.einstein.ceph import RBD
from ims.einstein.dnsmasq import DNSMasq
from ims.einstein.hil import HIL
from ims.einstein.iscsi.tgt import TGT
from ims.exception.exception import RegistrationFailedException, \
    FileSystemException, DBException, HILException, ISCSIException, \
    AuthorizationFailedException, DHCPException

logger = create_logger(__name__)


class BMI:
    @log
    def __init__(self, *args):
        if args.__len__() == 1:
            credentials = args[0]
            self.cfg = config.get()
            self.db = Database()
            self.__process_credentials(credentials)
            self.hil = HIL(
                base_url=self.cfg.net_isolator.url,
                usr=self.username,
                passwd=self.password)
            self.fs = RBD(self.cfg.fs,
                          self.cfg.iscsi.password)
            self.dhcp = DNSMasq()
            # self.iscsi = IET(self.fs, self.config.iscsi_update_password)
            # Need to make this generic by passing specific config
            self.iscsi = TGT(self.cfg.fs.conf_file,
                             self.cfg.fs.id,
                             self.cfg.fs.pool)
        elif args.__len__() == 3:
            username, password, project = args
            self.cfg = config.get()
            self.username = username
            self.password = password
            self.proj = project
            self.db = Database()
            self.pid = self.__does_project_exist(self.proj)
            self.is_admin = self.__check_admin()
            self.hil = HIL(
                base_url=self.cfg.net_isolator.url,
                usr=self.username,
                passwd=self.password)
            self.fs = RBD(self.cfg.fs,
                          self.cfg.iscsi.password)
            logger.debug("Username is %s and Password is %s", self.username,
                         self.password)
            self.dhcp = DNSMasq()
            # self.iscsi = IET(self.fs, self.config.iscsi_update_password)
            self.iscsi = TGT(self.cfg.fs.conf_file,
                             self.cfg.fs.id,
                             self.cfg.fs.pool)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @trace
    def __does_project_exist(self, project):
        pid = self.db.project.fetch_id_with_name(project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            logger.info("Raising Project Not Found Exception for %s",
                        project)
            raise db_exceptions.ProjectNotFoundException(project)

        return pid

    # this method will determine whether user is admin (still unclear on doing
    # it properly)
    def __check_admin(self):
        return True

    @trace
    def __get_ceph_image_name(self, name):
        img_id = self.db.image.fetch_id_with_name_from_project(name,
                                                               self.proj)
        if img_id is None:
            logger.info("Raising Image Not Found Exception for %s", name)
            raise db_exceptions.ImageNotFoundException(name)

        return str(self.cfg.bmi.uid) + "img" + str(img_id)

    def get_ceph_image_name_from_project(self, name, project_name):
        img_id = self.db.image.fetch_id_with_name_from_project(name,
                                                               project_name)
        if img_id is None:
            logger.info("Raising Image Not Found Exception for %s", name)
            raise db_exceptions.ImageNotFoundException(name)

        return str(self.cfg.bmi.uid) + "img" + str(img_id)

    @trace
    def __extract_id(self, ceph_img_name):
        start_index = ceph_img_name.find("img")
        start_index += 3
        img_id = ceph_img_name[start_index:]
        return img_id

    @trace
    def __process_credentials(self, credentials):
        base64_str, self.proj = credentials
        self.pid = self.__does_project_exist(self.proj)
        self.username, self.password = tuple(
            base64.b64decode(base64_str).split(':'))
        logger.debug("Username is %s and Password is %s", self.username,
                     self.password)
        self.is_admin = self.__check_admin()

    @log
    def __register(self, node_name, img_name, target_name, mac_addr):
        logger.debug("The Mac Addr File name is %s", mac_addr)
        self.__generate_ipxe_file(node_name, target_name)
        self.__generate_mac_addr_file(img_name, node_name, mac_addr)

    @log
    def __generate_ipxe_file(self, node_name, target_name):
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        logger.debug("Template LOC = %s", template_loc)
        path = self.cfg.tftp.ipxe_path + node_name + ".ipxe"
        logger.debug("The Path for ipxe file is %s", path)
        try:
            with open(path, 'w') as ipxe:
                for line in open(template_loc + "/ipxe.temp", 'r'):
                    line = line.replace(constants.IPXE_TARGET_NAME,
                                        target_name)
                    line = line.replace(constants.IPXE_ISCSI_IP,
                                        self.cfg.iscsi.ip)
                    ipxe.write(line)
            logger.info("Generated ipxe file")
            os.chmod(path, 0755)
            logger.info("Changed permissions to 755")
        except (OSError, IOError) as e:
            logger.info("Raising Registration Failed Exception for %s",
                        node_name)
            raise RegistrationFailedException(node_name, e.message)

    @log
    def __generate_mac_addr_file(self, img_name, node_name, mac_addr):
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        logger.debug("Template LOC = %s", template_loc)
        path = self.cfg.tftp.pxelinux_path + mac_addr
        logger.debug("The Path for mac addr file is %s", path)
        try:
            with open(path, 'w') as mac:
                for line in open(template_loc + "/mac.temp", 'r'):
                    line = line.replace(constants.MAC_IMG_NAME, img_name)
                    line = line.replace(constants.MAC_IPXE_NAME,
                                        node_name + ".ipxe")
                    mac.write(line)
            logger.info("Generated mac addr file")
            os.chmod(path, 0644)
            logger.debug("Changed permissions to 644")
        except (OSError, IOError) as e:
            logger.info("Raising Registration Failed Exception for %s",
                        node_name)
            raise RegistrationFailedException(node_name, e.message)

    # Parses the Exception and returns the dict that should be returned to user
    @log
    def __return_error(self, ex):

        # Replaces the image name with id in error string
        @log
        def swap_id_with_name(err_str):
            parts = err_str.split(" ")
            start_index = parts[0].find("img")
            if start_index != -1:
                start_index += 3
                img_id = parts[0][start_index:]
                name = self.db.image.fetch_name_with_id(img_id)
                if name is not None:
                    parts[0] = name
            return " ".join(parts)

        logger.debug("Checking if FileSystemException")
        if FileSystemException in ex.__class__.__bases__:
            logger.debug("It is FileSystemException")
            return {constants.STATUS_CODE_KEY: ex.status_code,
                    constants.MESSAGE_KEY: swap_id_with_name(str(ex))}

        return {constants.STATUS_CODE_KEY: ex.status_code,
                constants.MESSAGE_KEY: str(ex)}

    # A custom function which is wrapper around only success code that
    # we are creating.
    @log
    def __return_success(self, obj):
        return {constants.STATUS_CODE_KEY: 200,
                constants.RETURN_VALUE_KEY: obj}

    @log
    def shutdown(self):
        self.fs.tear_down()
        self.db.close()

    # Provisions from HIL and Boots the given node with given image
    @log
    def provision(self, node_name, img_name, network, nic):
        try:
            mac_addr = "01-" + self.hil.get_node_mac_addr(node_name). \
                replace(":", "-")
            self.hil.attach_node_to_project_network(node_name, network, nic)

            parent_id = self.db.image.fetch_id_with_name_from_project(img_name,
                                                                      self.proj
                                                                      )
            self.db.image.insert(node_name, self.pid, parent_id)
            clone_ceph_name = self.__get_ceph_image_name(node_name)
            ceph_img_name = self.__get_ceph_image_name(img_name)
            self.fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME,
                          clone_ceph_name)
            ceph_config = self.cfg.fs
            logger.debug("Contents of ceph_config = %s", str(ceph_config))
            self.iscsi.add_target(clone_ceph_name)
            logger.info("The create command was executed successfully")
            self.__register(node_name, img_name, clone_ceph_name, mac_addr)
            return self.__return_success(True)

        except RegistrationFailedException as e:
            # Message is being handled by custom formatter
            # TODO: add a deployment and a unit test for this case.
            logger.exception('')
            clone_ceph_name = self.__get_ceph_image_name(node_name)
            self.iscsi.remove_target(clone_ceph_name)
            self.fs.remove(clone_ceph_name)
            self.db.image.delete_with_name_from_project(node_name, self.proj)
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.detach_node_from_project_network(node_name, network,
                                                      nic)
            return self.__return_error(e)

        except ISCSIException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            clone_ceph_name = self.__get_ceph_image_name(node_name)
            self.fs.remove(clone_ceph_name)
            self.db.image.delete_with_name_from_project(node_name, self.proj)
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.detach_node_from_project_network(node_name, network,
                                                      nic)
            return self.__return_error(e)

        except FileSystemException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            self.db.image.delete_with_name_from_project(node_name, self.proj)
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.detach_node_from_project_network(node_name, network,
                                                      nic)
            return self.__return_error(e)
        except DBException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.detach_node_from_project_network(node_name, network,
                                                      nic)
            return self.__return_error(e)
        except HILException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            return self.__return_error(e)

    # This is for detach a node and removing it from iscsi
    # and destroying its image
    @log
    def deprovision(self, node_name, network, nic):
        ceph_img_name = None
        try:
            self.hil.detach_node_from_project_network(node_name,
                                                      network, nic)
            ceph_img_name = self.__get_ceph_image_name(node_name)
            self.db.image.delete_with_name_from_project(node_name, self.proj)
            ceph_config = self.cfg.fs
            logger.debug("Contents of ceph+config = %s", str(ceph_config))
            self.iscsi.remove_target(ceph_img_name)
            logger.info("The delete command was executed successfully")
            ret = self.fs.remove(str(ceph_img_name).encode("utf-8"))
            return self.__return_success(ret)

        except FileSystemException as e:
            logger.exception('')
            self.iscsi.add_target(ceph_img_name)
            parent_name = self.fs.get_parent_info(ceph_img_name)[1]

            parent_id = self.db.image.fetch_id_with_name_from_project(
                parent_name,
                self.proj)
            self.db.image.insert(node_name, self.pid, parent_id,
                                 id=self.__extract_id(ceph_img_name))
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.attach_node_to_project_network(node_name, network, nic)
            return self.__return_error(e)
        except ISCSIException as e:
            logger.exception('')
            parent_name = self.fs.get_parent_info(ceph_img_name)[1]
            parent_id = self.db.image.fetch_id_with_name_from_project(
                parent_name,
                self.proj)
            self.db.image.insert(node_name, self.pid, parent_id,
                                 id=self.__extract_id(ceph_img_name))
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.attach_node_to_project_network(node_name, network, nic)
            return self.__return_error(e)
        except DBException as e:
            logger.exception('')
            time.sleep(constants.HIL_CALL_TIMEOUT)
            self.hil.attach_node_to_project_network(node_name, network, nic)
            return self.__return_error(e)
        except HILException as e:
            logger.exception('')
            return self.__return_error(e)

    # Creates snapshot for the given image with snap_name as given name
    # fs_obj will be populated by decorator
    @log
    def create_snapshot(self, node_name, snap_name):
        try:
            self.hil.validate_project(self.proj)

            ceph_img_name = self.__get_ceph_image_name(node_name)

            self.fs.snap_image(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(ceph_img_name,
                                 constants.DEFAULT_SNAPSHOT_NAME)
            parent_id = self.db.image.fetch_parent_id(self.proj, node_name)
            self.db.image.insert(snap_name, self.pid, parent_id,
                                 is_snapshot=True)
            snap_ceph_name = self.__get_ceph_image_name(snap_name)
            self.fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME,
                          snap_ceph_name)
            self.fs.flatten(snap_ceph_name)
            self.fs.snap_image(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(snap_ceph_name,
                                 constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_unprotect(ceph_img_name,
                                   constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.remove_snapshot(ceph_img_name,
                                    constants.DEFAULT_SNAPSHOT_NAME)
            return self.__return_success(True)

        except (HILException, DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    # Lists snapshot for the given image img_name
    # URL's have to be read from BMI config file
    # fs_obj will be populated by decorator
    @log
    def list_snapshots(self):
        try:
            self.hil.validate_project(self.proj)
            snapshots = self.db.image.fetch_snapshots_from_project(self.proj)
            return self.__return_success(snapshots)

        except (HILException, DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    # Removes snapshot snap_name for the given image img_name
    # fs_obj will be populated by decorator
    @log
    def remove_image(self, img_name):
        try:
            self.hil.validate_project(self.proj)
            ceph_img_name = self.__get_ceph_image_name(img_name)

            self.fs.snap_unprotect(ceph_img_name,
                                   constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.remove_snapshot(ceph_img_name,
                                    constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.remove(ceph_img_name)
            self.db.image.delete_with_name_from_project(img_name, self.proj)
            return self.__return_success(True)
        except (HILException, DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    # Lists the images for the project which includes the snapshot
    @log
    def list_images(self):
        try:
            self.hil.validate_project(self.proj)
            names = self.db.image.fetch_images_from_project(self.proj)
            return self.__return_success(names)

        except (HILException, DBException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def list_provisioned_nodes(self):
        try:
            clones = self.db.image.fetch_clones_from_project(self.proj)
            return self.__return_success(clones)
        except DBException as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def list_all_images(self):
        try:
            images = self.db.image.fetch_all_images()
            new_images = []
            for image in images:
                image.insert(3, self.get_ceph_image_name_from_project(image[1],
                                                                      image[
                                                                          2]))
                new_images.append(image)
            return self.__return_success(new_images)
        except DBException as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def import_ceph_image(self, img):
        """
        Import an image from ceph to be used by BMI

        Clone an image in ceph to be used by BMI.

        :param img: Name of image in ceph
        :return: True on successful completion
        """

        try:
            ceph_img_name = str(img)

            # create a snapshot of the golden image and protect it
            # this is needed because, in ceph, you can only create clones from
            # snapshots.
            self.fs.snap_image(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(ceph_img_name,
                                 constants.DEFAULT_SNAPSHOT_NAME)

            # insert golden image name into bmi db
            self.db.image.insert(ceph_img_name, self.pid)

            # get a name for our copy of the golden image. For instance an
            # image in ceph called centos6.7, after cloning, will be a given
            # a name like 4img1 based on the UID in config and image id in db
            snap_ceph_name = self.__get_ceph_image_name(ceph_img_name)

            # clone the snapshot of the golden image and then flatten it
            self.fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME,
                          snap_ceph_name)
            self.fs.flatten(snap_ceph_name)

            # create a snapshot of our newly created golden image so that when
            # we provision, we can easily make clones from this readily
            # available snapshot.
            self.fs.snap_image(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(snap_ceph_name,
                                 constants.DEFAULT_SNAPSHOT_NAME)

            # unprotect and delete the snapshot of the original golden because
            # we no longer need it.
            self.fs.snap_unprotect(ceph_img_name,
                                   constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.remove_snapshot(ceph_img_name,
                                    constants.DEFAULT_SNAPSHOT_NAME)
            return self.__return_success(True)
        except (DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def import_ceph_snapshot(self, img, snap_name, protect):
        """
        Import a snapshot from ceph to be used by BMI

        Clone a snapshot in ceph to be used by BMI. Similar to
        import_ceph_image except we can directly start the cloning process
        because it is already a snapshot.

        :param img: Name of snapshot in ceph
        :return: True on successful completion
        """
        try:
            ceph_img_name = str(img)

            if protect:
                self.fs.snap_protect(ceph_img_name, snap_name)
            self.db.image.insert(ceph_img_name, self.pid)
            snap_ceph_name = self.__get_ceph_image_name(ceph_img_name)
            self.fs.clone(ceph_img_name, snap_name,
                          snap_ceph_name)
            self.fs.flatten(snap_ceph_name)
            self.fs.snap_image(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(snap_ceph_name,
                                 constants.DEFAULT_SNAPSHOT_NAME)
            return self.__return_success(True)
        except (DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def export_ceph_image(self, img, name):
        try:
            ceph_img_name = self.__get_ceph_image_name(img)
            self.fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME, name)
            self.fs.flatten(name)
            return self.__return_success(True)
        except FileSystemException as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def delete_image(self, project, img):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            self.db.image.delete_with_name_from_project(img, project)
            return self.__return_success(True)
        except (DBException, AuthorizationFailedException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def add_image(self, project, img, id, snap, parent, public):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            parent_id = None
            if parent is not None:
                parent_id = self.db.image.fetch_id_with_name_from_project(
                    parent,
                    project)
            pid = self.__does_project_exist(project)
            self.db.image.insert(img, pid, parent_id, public, snap, id)
            return self.__return_success(True)
        except (DBException, AuthorizationFailedException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def get_node_ip(self, node_name):
        try:
            mac_addr = self.hil.get_node_mac_addr(node_name)
            return self.__return_success(self.dhcp.get_ip(mac_addr))
        except (HILException, DHCPException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def copy_image(self, img1, dest_project, img2=None):
        """
        Create a deep copy of src image

        :param img1: Name of src image
        :param dest_project: Name of the project where des image will be
        created
        :param img2: Name of des image
        :return: True on successful completion
        """
        try:
            if not self.is_admin and (self.proj != dest_project):
                raise AuthorizationFailedException()
            dest_pid = self.__does_project_exist(dest_project)
            self.db.image.copy_image(self.proj, img1, dest_pid, img2)
            if img2 is not None:
                ceph_name = self.get_ceph_image_name_from_project(img2,
                                                                  dest_project)
            else:
                ceph_name = self.get_ceph_image_name_from_project(img1,
                                                                  dest_project)
            self.fs.clone(self.get_ceph_image_name_from_project(
                img1, self.proj),
                constants.DEFAULT_SNAPSHOT_NAME,
                ceph_name)

            self.fs.flatten(ceph_name)
            self.fs.snap_image(ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(ceph_name, constants.DEFAULT_SNAPSHOT_NAME)

            return self.__return_success(True)
        except (DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def move_image(self, img1, dest_project, img2):
        try:
            if not self.is_admin and (self.proj != dest_project):
                raise AuthorizationFailedException()
            dest_pid = self.__does_project_exist(dest_project)
            self.db.image.move_image(self.proj, img1, dest_pid, img2)
            return self.__return_success(True)
        except DBException as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def add_project(self, project, network, id):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            self.db.project.insert(project, network, id)
            return self.__return_success(True)
        except (DBException, AuthorizationFailedException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def delete_project(self, project):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            self.db.project.delete_with_name(project)
            return self.__return_success(True)
        except (DBException, AuthorizationFailedException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def list_projects(self):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            projects = self.db.project.fetch_projects()
            return self.__return_success(projects)
        except (DBException, AuthorizationFailedException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def mount_image(self, img):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            ceph_img_name = self.__get_ceph_image_name(img)
            self.iscsi.add_target(ceph_img_name)
            return self.__return_success(True)
        except (ISCSIException, DBException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def umount_image(self, img):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            ceph_img_name = self.__get_ceph_image_name(img)
            self.iscsi.remove_target(ceph_img_name)
            return self.__return_success(True)
        except (ISCSIException, DBException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def show_mounted(self):
        try:
            if not self.is_admin:
                raise AuthorizationFailedException()
            mappings = self.iscsi.list_targets()
            swapped_mappings = {}
            for k, v in mappings.iteritems():
                img_id = self.__extract_id(k)
                if self.proj == self.db.image.fetch_project_with_id(img_id):
                    swapped_mappings[
                        self.db.image.fetch_name_with_id(img_id)] = v
            return self.__return_success(swapped_mappings)
        except (ISCSIException, DBException) as e:
            logger.exception('')
            return self.__return_error(e)

    @log
    def remake_mappings(self):
        try:
            self.iscsi.persist_targets()
        except (FileSystemException, ISCSIException) as e:
            logger.exception('')
        except NotImplementedError:
            pass
