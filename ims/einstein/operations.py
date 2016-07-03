#!/usr/bin/python
import base64
import io
import subprocess
import time

from ims.database import *
from ims.einstein.ceph import *
from ims.einstein.haas import *
from ims.exception import *

logger = create_logger(__name__)


class BMI:
    @log
    def __init__(self, credentials):
        self.config = config.get()
        self.db = Database()
        self.__process_credentials(credentials)
        self.haas = HaaS(base_url=self.config.haas_url, usr=self.username,
                         passwd=self.password)
        self.fs = RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @trace
    def __does_project_exist(self):
        pid = self.db.project.fetch_id_with_name(self.project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            logger.info("Raising Project Not Found Exception for %s",
                        self.project)
            raise db_exceptions.ProjectNotFoundException(self.project)

        self.pid = pid

    @trace
    def __get__ceph_image_name(self, name):
        img_id = self.db.image.fetch_id_with_name_from_project(name,
                                                               self.project)
        if img_id is None:
            logger.info("Raising Image Not Found Exception for %s", name)
            raise db_exceptions.ImageNotFoundException(name)

        return str(self.config.uid) + "img" + str(img_id)

    @trace
    def __process_credentials(self, credentials):
        base64_str, self.project = credentials
        self.__does_project_exist()
        self.username, self.password = tuple(
            base64.b64decode(base64_str).split(':'))
        logger.debug("Username is %s and Password is %s", self.username,
                     self.password)

    @log
    def __register(self, node_name, img_name, target_name):
        mac_addr = "01-" + self.haas.get_node_mac_addr(node_name).replace(":",
                                                                          "-")
        logger.debug("The Mac Addr File name is %s", mac_addr)
        self.__generate_ipxe_file(node_name, target_name)
        self.__generate_mac_addr_file(img_name, node_name, mac_addr)

    @log
    def __generate_ipxe_file(self, node_name, target_name):
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        logger.debug("Template LOC = %s", template_loc)
        path = self.config.ipxe_loc + node_name + ".ipxe"
        logger.debug("The Path for ipxe file is %s", path)
        with io.open(path, 'w') as ipxe:
            for line in io.open(template_loc + "/ipxe.temp", 'r'):
                line = line.replace(constants.IPXE_TARGET_NAME, target_name)
                ipxe.write(line)
        logger.info("Generated ipxe file")
        os.chmod(path, 0755)
        logger.info("Changed permissions to 755")

    @log
    def __generate_mac_addr_file(self, img_name, node_name, mac_addr):
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        logger.debug("Template LOC = %s", template_loc)
        path = self.config.pxelinux_loc + mac_addr
        logger.debug("The Path for mac addr file is %s", path)
        with io.open(path, 'w') as mac:
            for line in io.open(template_loc + "/mac.temp", 'r'):
                line = line.replace(constants.MAC_IMG_NAME, img_name)
                line = line.replace(constants.MAC_IPXE_NAME,
                                    node_name + ".ipxe")
                mac.write(line)
        logger.info("Generated mac addr file")
        os.chmod(path, 0644)
        logger.debug("Changed permissions to 644")

    # Calling shell script which executes a iscsi update as we don't have
    # rbd map in documentation.
    @log
    def __call_shellscript(self, *args):
        arglist = list(args)
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        logger.debug("Created Process with pid = %s", proc.pid)
        return proc.communicate()

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

    # Provisions from HaaS and Boots the given node with given image
    @log
    def provision(self, node_name, img_name, network, channel, nic):
        try:
            self.haas.attach_node_to_project_network(node_name, network,
                                                     channel, nic)

            self.db.image.insert(node_name, self.pid, is_provision_clone=True)
            clone_ceph_name = self.__get__ceph_image_name(node_name)
            ceph_img_name = self.__get__ceph_image_name(img_name)
            self.fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME,
                          clone_ceph_name)
            ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
            logger.debug("Contents of ceph_config = %s", str(ceph_config))
            # Should be changed to python script
            iscsi_output = self.__call_shellscript(
                self.config.iscsi_update,
                ceph_config[
                    constants.CEPH_KEY_RING_KEY],
                ceph_config[
                    constants.CEPH_ID_KEY],
                ceph_config[
                    constants.CEPH_POOL_KEY],
                str(clone_ceph_name),
                constants.ISCSI_CREATE_COMMAND,
                self.config.iscsi_update_password)
            if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                logger.info("The create command was executed successfully")
                self.__register(node_name, img_name, clone_ceph_name)
                return self.__return_success(True)

            elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                # Was not able to test this exception in test cases as the haas
                # call was blocking this exception
                # But it was raised during preparation of tests
                # Rare exception
                logger.info("Raising Node Already In Use Exception")
                raise iscsi_exceptions.NodeAlreadyInUseException()

        except ISCSIException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            clone_ceph_name = self.__get__ceph_image_name(node_name)
            self.fs.remove(clone_ceph_name)
            self.db.image.delete_with_name_from_project(node_name, self.project)
            time.sleep(30)
            self.haas.detach_node_from_project_network(node_name, network,
                                                       nic)
            return self.__return_error(e)

        except FileSystemException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            self.db.image.delete_with_name_from_project(node_name, self.project)
            time.sleep(30)
            self.haas.detach_node_from_project_network(node_name, network,
                                                       nic)
            return self.__return_error(e)
        except DBException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            time.sleep(30)
            self.haas.detach_node_from_project_network(node_name, network,
                                                       nic)
            return self.__return_error(e)
        except HaaSException as e:
            # Message is being handled by custom formatter
            logger.exception('')
            return self.__return_error(e)

    # This is for detach a node and removing it from iscsi
    # and destroying its image
    @log
    def deprovision(self, node_name, network, nic):
        try:
            self.haas.detach_node_from_project_network(node_name,
                                                       network, nic)
            ceph_img_name = self.__get__ceph_image_name(node_name)
            self.db.image.delete_with_name_from_project(node_name, self.project)
            ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
            logger.debug("Contents of ceph+config = %s", str(ceph_config))
            iscsi_output = self.__call_shellscript(
                self.config.iscsi_update,
                ceph_config[
                    constants.CEPH_KEY_RING_KEY],
                ceph_config[
                    constants.CEPH_ID_KEY],
                ceph_config[
                    constants.CEPH_POOL_KEY],
                str(ceph_img_name),
                constants.ISCSI_DELETE_COMMAND,
                self.config.iscsi_update_password)
            if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                logger.info("The delete command was executed successfully")
                ret = self.fs.remove(str(ceph_img_name).encode("utf-8"))
                return self.__return_success(ret)

            elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                logger.info("Raising Node Already Unmapped Exception")
                raise iscsi_exceptions.NodeAlreadyUnmappedException()
        except FileSystemException as e:
            logger.exception('')
            iscsi_output = BMI.__call_shellscript(
                self.config.iscsi_update,
                ceph_config[
                    constants.CEPH_KEY_RING_KEY],
                ceph_config[
                    constants.CEPH_ID_KEY],
                ceph_config[
                    constants.CEPH_POOL_KEY],
                str(ceph_img_name),
                constants.ISCSI_CREATE_COMMAND,
                self.config.iscsi_update_password)
            self.db.image.insert(node_name, self.pid, is_provision_clone=True,
                                 id=ceph_img_name[3:])
            time.sleep(30)
            self.haas.attach_node_haas_project(self.project, node_name)
            return self.__return_error(e)
        except ISCSIException as e:
            logger.exception('')
            self.db.image.insert(node_name, self.pid, is_provision_clone=True,
                                 id=ceph_img_name[3:])
            time.sleep(30)
            self.haas.attach_node_haas_project(self.project, node_name)
            return self.__return_error(e)
        except DBException as e:
            logger.exception('')
            time.sleep(30)
            self.haas.attach_node_haas_project(self.project, node_name)
            return self.__return_error(e)
        except HaaSException as e:
            logger.exception('')
            return self.__return_error(e)

    # Creates snapshot for the given image with snap_name as given name
    # fs_obj will be populated by decorator
    @log
    def create_snapshot(self, node_name, snap_name):
        try:
            self.haas.validate_project(self.project)

            ceph_img_name = self.__get__ceph_image_name(node_name)

            self.fs.snap_image(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.snap_protect(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.db.image.insert(snap_name, self.pid, is_snapshot=True)
            snap_ceph_name = self.__get__ceph_image_name(snap_name)
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

        except (HaaSException, DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    # Lists snapshot for the given image img_name
    # URL's have to be read from BMI config file
    # fs_obj will be populated by decorator
    @log
    def list_snapshots(self):
        try:
            self.haas.validate_project(self.project)
            snapshots = self.db.image.fetch_snapshots_from_project(self.project)
            return self.__return_success(snapshots)

        except (HaaSException, DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    # Removes snapshot snap_name for the given image img_name
    # fs_obj will be populated by decorator
    @log
    def remove_image(self, img_name):
        try:
            self.haas.validate_project(self.project)
            ceph_img_name = self.__get__ceph_image_name(img_name)

            self.fs.snap_unprotect(ceph_img_name,
                                   constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.remove_snapshot(ceph_img_name,
                                    constants.DEFAULT_SNAPSHOT_NAME)
            self.fs.remove(ceph_img_name)
            self.db.image.delete_with_name_from_project(img_name, self.project)
            return self.__return_success(True)
        except (HaaSException, DBException, FileSystemException) as e:
            logger.exception('')
            return self.__return_error(e)

    # Lists the images for the project which includes the snapshot
    @log
    def list_images(self):
        try:
            self.haas.validate_project(self.project)
            names = self.db.image.fetch_images_from_project(self.project)
            return self.__return_success(names)

        except (HaaSException, DBException) as e:
            logger.exception('')
            return self.__return_error(e)
