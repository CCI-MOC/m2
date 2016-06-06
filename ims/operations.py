#!/usr/bin/python
import io
import subprocess

from ceph_wrapper import *
from config import BMIConfig
from database import *
from haas_wrapper import *
from log import *


# logging will be submitted later

class BMI:
    def __init__(self, usr, passwd, debug=False, verbose=False):
        self.config = self.__create_config()
        self.haas = HaaS(base_url=self.config.haas_url, usr=usr, passwd=passwd)
        self.logger = create_logger("ims.einstein.operations", debug, verbose)

    # Provisions from HaaS and Boots the given node with given image
    def provision(self, node_name, img_name="hadoopMaster.img",
                  snap_name="HadoopMasterGoldenImage",
                  network="bmi-provision"):
        try:
            self.logger.debug("Entered Provision")
            self.logger.debug(
                "Got parameters = %s %s %s %s", node_name, img_name,
                snap_name, network)
            self.logger.info(
                "Attaching Node %s to network %s", node_name, network)
            self.haas.attach_node_to_project_network(node_name, network)
            self.logger.info("Successfully Attached Node %s to network %s",
                             node_name, network)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                self.logger.info(
                    "Cloning snap %s under %s as %s", snap_name, img_name,
                    node_name)
                ret = fs.clone(img_name.encode('utf-8'),
                               snap_name.encode('utf-8'),
                               node_name.encode("utf-8"))
                self.logger.info(
                    "Successfully Finished Cloning snap %s under %s as %s",
                    snap_name, img_name,
                    node_name)

                ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
                self.logger.debug("Contents of ceph_config = %s",
                                  str(ceph_config))
                # Should be changed to python script
                self.logger.info(
                    "Calling ISCSI shellscript with create command")
                iscsi_output = self.__call_shellscript(self.config.iscsi_update,
                                                       ceph_config[
                                                           constants.CEPH_KEY_RING_KEY],
                                                       ceph_config[
                                                           constants.CEPH_ID_KEY],
                                                       ceph_config[
                                                           constants.CEPH_POOL_KEY],
                                                       node_name,
                                                       constants.ISCSI_CREATE_COMMAND)
                if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                    self.logger.info("The create command was done successfully")
                    return self.__return_success(ret)
                elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                    # Was not able to test this exception in test cases as the haas
                    # call was blocking this exception
                    # But it was raised during preparation of tests
                    # Rare exception
                    self.logger.debug("Raising Node Already In Use Exception")
                    raise iscsi_exceptions.NodeAlreadyInUseException()

        except (HaaSException, ISCSIException, FileSystemException) as e:
            self.logger.exception(
                '')  # Message is being handled by custom formatter
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Provision")

    # This is for detach a node and removing it from iscsi
    # and destroying its image
    def detach_node(self, node_name, network="bmi-provision"):
        try:
            self.logger.debug("Entering Detach Node")
            self.logger.debug("Got parameters = %s %s", node_name, network)

            self.logger.info("Detaching node %s from network %s", node_name,
                             network)
            self.haas.detach_node_from_project_network(node_name,
                                                       network)
            self.logger.info("Successfully detached node %s from network %s",
                             node_name, network)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]

                self.logger.debug("Contents of ceph+config = %s",
                                  str(ceph_config))
                self.logger.info(
                    "Calling ISCSI Shellscript with delete command")
                iscsi_output = self.__call_shellscript(self.config.iscsi_update,
                                                       ceph_config[
                                                           constants.CEPH_KEY_RING_KEY],
                                                       ceph_config[
                                                           constants.CEPH_ID_KEY],
                                                       ceph_config[
                                                           constants.CEPH_POOL_KEY],
                                                       node_name,
                                                       constants.ISCSI_DELETE_COMMAND)
                if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                    self.logger.info(
                        "The delete command was executed successfully")
                    self.logger.info("Removing Image %s", node_name)
                    ret = fs.remove(node_name.encode("utf-8"))
                    self.logger.info("Successfully Removed Image %s", node_name)
                    return self.__return_success(ret)
                elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                    self.logger.debug("Raising Node Already Unmapped Exception")
                    raise iscsi_exceptions.NodeAlreadyUnmappedException()
        except (HaaSException, ISCSIException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Detach Node")

    # Creates snapshot for the given image with snap_name as given name
    # fs_obj will be populated by decorator
    def create_snapshot(self, project, img_name, snap_name):
        try:
            self.logger.debug("Entered Create Snapshot")
            self.logger.debug("Got parameters = %s %s %s", project, img_name,
                              snap_name)

            self.logger.info("Authenticating project %s", project)
            self.haas.validate_project(project)
            self.logger.info("Successfully Authenticated project %s", project)

            self.logger.debug("Checking whether project %s in db", project)
            self.__does_project_exist(project)
            self.logger.debug("project %s is in db", project)

            self.logger.debug("Getting image id for image %s in project %s",
                              img_name, project)
            img_id = self.__get_image_id(project, img_name)
            self.logger.debug("Got img_id = %s for image %s in project %s",
                              img_id, img_name, project)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                self.logger.info("Creating Snapshot of image %s with name %s",
                                 img_name, snap_name)
                ret = fs.snap_image(img_id, snap_name)
                self.logger.info(
                    "Successfully Created Snapshot of image %s with name %s",
                    img_name, snap_name)
                return self.__return_success(ret)

        except (HaaSException, DBException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Create Snapshot")

    # Lists snapshot for the given image img_name
    # URL's have to be read from BMI config file
    # fs_obj will be populated by decorator
    def list_snaps(self, project, img_name):
        try:
            self.logger.debug("Entered List Snapshots")
            self.logger.debug("Got parameters = %s %s", project, img_name)

            self.logger.info("Authenticating project %s", project)
            self.haas.validate_project(project)
            self.logger.info("Successfully Authenticated project %s", project)

            self.logger.debug("Checking whether project %s in db", project)
            self.__does_project_exist(project)
            self.logger.debug("project %s is in db", project)

            self.logger.debug("Getting image id for image %s in project %s",
                              img_name, project)
            img_id = self.__get_image_id(project, img_name)
            self.logger.debug("Got img_id = %s for image %s in project %s",
                              img_id, img_name, project)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                self.logger.info("Getting Snapshots for image %s in project %s",
                                 img_name, project)
                snapshots = fs.list_snapshots(img_id)
                self.logger.info(
                    "Successfully Got Snapshots for image %s in project %s",
                    img_name, project)
                self.logger.debug("Snapshots = %s", str(snapshots))
                return self.__return_success(snapshots)

        except (HaaSException, DBException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting List Snapshots")

    # Removes snapshot snap_name for the given image img_name
    # fs_obj will be populated by decorator
    def remove_snaps(self, project, img_name, snap_name):
        try:
            self.logger.debug("Entered Remove Snaps")
            self.logger.debug("Got parameters = %s %s %s", project, img_name,
                              snap_name)

            self.logger.info("Authenticating project %s", project)
            self.haas.validate_project(project)
            self.logger.info("Successfully Authenticated project %s", project)

            self.logger.debug("Checking whether project %s in db", project)
            self.__does_project_exist(project)
            self.logger.debug("project %s is in db", project)

            self.logger.debug("Getting image id for image %s in project %s",
                              img_name, project)
            img_id = self.__get_image_id(project, img_name)
            self.logger.debug("Got img_id = %s for image %s in project %s",
                              img_id, img_name, project)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                self.logger.info(
                    "Removing snapshot %s for image %s in project %s",
                    snap_name, img_name, project)
                ret = fs.remove_snapshots(img_id, snap_name)
                self.logger.info(
                    "Successfully Removed snapshot %s for image %s in project %s",
                    snap_name, img_name, project)
                return self.__return_success(ret)

        except (HaaSException, DBException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Remove Snaps")

    # Lists the images for the project which includes the snapshot
    def list_all_images(self, project):
        try:

            self.logger.debug("Entered List All Images")
            self.logger.debug("Got parameters = %s", project)

            self.logger.info("Authenticating project %s", project)
            self.haas.validate_project(project)
            self.logger.info("Successfully Authenticated project %s", project)

            self.logger.debug("Checking whether project %s in db", project)
            self.__does_project_exist(project)
            self.logger.debug("project %s is in db", project)

            imgr = ImageRepository()
            self.logger.info("Fetching names from db for project %s", project)
            names = imgr.fetch_names_from_project(project)
            self.logger.info("Got names successfully from db for project %s",
                             project)
            self.logger.debug("Names = %s", str(names))
            return self.__return_success(names)
        except (HaaSException, DBException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting List All Images")

    # Need to make it is in working order before logging
    def register_node(self, node_name):
        node_num = node_name.split("-")[1].lstrip("0")
        ip_addr = "192.168.29." + node_num
        mac_addr = "01-" + self.haas.get_node_mac_addr(node_name).replace(":",
                                                                          "-")
        self.__generate_mac_addr_file(node_name, ip_addr, mac_addr)

    def __generate_mac_addr_file(self, node_name, ip_addr, mac_addr,
                                 template_loc="test.txt"):
        config = io.open(mac_addr, 'w')
        for line in io.open(template_loc, 'r'):
            line = line.replace('${ip_addr}', ip_addr)
            line = line.replace('${node_name}', node_name)
            config.write(line)
        config.close()

    def __does_project_exist(self, name):
        self.logger.debug("Entering Does Project Exist")
        self.logger.debug("Got parameters = %s",name)
        pr = ProjectRepository()
        self.logger.debug("Getting pid for project %s",name)
        pid = pr.fetch_id_with_name(name)
        self.logger.debug("Got pid = %s for project %s",str(pid),name)
        # None as a query result implies that the project does not exist.
        if pid is None:
            self.logger.debug("Raising Project Not Found Exception")
            raise db_exceptions.ProjectNotFoundException(name)
        self.logger.debug("Exiting Does Project Exist")

    def __get_image_id(self, project, name):
        self.logger.debug("Entering Get Image Id")
        self.logger.debug("Got parameters = %s %s",project,name)
        imgr = ImageRepository()
        self.logger.debug("Getting img_id for image %s",name)
        img_id = imgr.fetch_id_with_name_from_project(name, project)
        self.logger.debug("Got id = %s ")
        if img_id is None:
            raise db_exceptions.ImageNotFoundException(name)
        return str(img_id)

    # Calling shell script which executes a iscsi update as we don't have
    # rbd map in documentation.
    def __call_shellscript(*args):
        arglist = list(args)
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return proc.communicate()

    # Creates a filesystem configuration object
    def __create_config(self):
        try:
            config = BMIConfig()
            config.parse_config()
            return config
        except ConfigException:  # Should be logged
            raise  # Crashing it for now

    # A custom function which is wrapper around only success code that
    # we are creating.
    def __return_success(self, obj):
        return {constants.STATUS_CODE_KEY: 200, constants.RETURN_VALUE_KEY: obj}

    # Parses the Exception and returns the dict that should be returned to user
    def __return_error(self, ex):
        ex_parser = ExceptionParser()
        if FileSystemException in ex.__class__.__bases__:
            return {constants.STATUS_CODE_KEY: ex_parser.parse(ex),
                    constants.MESSAGE_KEY: self.__swap_id_with_name(str(ex))}
        return {constants.STATUS_CODE_KEY: ex_parser.parse(ex),
                constants.MESSAGE_KEY: str(ex)}

    # Replaces the image name with id in error string
    def __swap_id_with_name(self, err_str):
        parts = err_str.split(" ")
        imgr = ImageRepository()
        name = imgr.fetch_name_with_id(parts[0].strip())
        if name is not None:
            parts[0] = name
        return " ".join(parts)
