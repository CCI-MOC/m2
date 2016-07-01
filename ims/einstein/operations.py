#!/usr/bin/python
import base64
import io
import subprocess
import time

import ims.common.config as config
from ims.common.log import *
from ims.database import *
from ims.einstein.ceph import *
from ims.einstein.haas import *
from ims.exception import *



class BMI:
    def __init__(self, credentials):
        self.config = config.get()
        self.logger = create_logger(self.config.logs_url, __name__,
                                    self.config.logs_debug,
                                    self.config.logs_verbose)
        self.logger.info("Initialising DB")
        self.db = Database()
        self.logger.info("Initialised DB")
        self.logger.info("Processing Credentials")
        self.__process_credentials(credentials)
        self.logger.info("Processed Credentials")
        self.logger.info("Initializing HaaS")
        self.haas = HaaS(base_url=self.config.haas_url, usr=self.username,
                         passwd=self.password)
        self.logger.info("Initialized HaaS")
        self.logger.info("Initializing File System")
        self.fs = RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME])
        self.logger.info("Initialized File System")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def __does_project_exist(self):
        self.logger.debug("Entered does project exist")
        self.logger.debug("Fetching id of project %s", self.project)
        pid = self.db.project.fetch_id_with_name(self.project)
        self.logger.debug("Got id = %s", pid)
        # None as a query result implies that the project does not exist.
        if pid is None:
            self.logger.info("Raising Project Not Found Exception")
            raise db_exceptions.ProjectNotFoundException(self.project)

        self.pid = pid
        self.logger.debug("Exiting does project exist")

    def __get__ceph_image_name(self, name):
        self.logger.debug("Entered get ceph image name")
        self.logger.debug("Fetching image id with name %s under project %s")
        img_id = self.db.image.fetch_id_with_name_from_project(name,
                                                               self.project)
        self.logger.debug("Got id = %s", img_id)
        if img_id is None:
            self.logger.debug("Raising Image Not Found Exception")
            raise db_exceptions.ImageNotFoundException(name)

        img_name = str(self.config.uid) + "img" + str(img_id)
        self.logger.debug("the img_name is %s", img_name)
        self.logger.debug("Exiting get ceph image name")
        return img_name

    def __process_credentials(self, credentials):
        self.logger.debug("Entered process credentials")
        self.logger.debug("Got parameter = %s", credentials)
        base64_str, self.project = credentials
        self.logger.info("Project received is %s", self.project)
        self.logger.info("base64 string is %s", base64_str)
        self.logger.debug("Checking if project exists")
        self.__does_project_exist()
        self.logger.debug("Project Exists")
        self.username, self.password = tuple(
            base64.b64decode(base64_str).split(':'))
        self.logger.info("the HaaS username and password are %s %s",
                         self.username, self.password)
        self.logger.debug("Exiting process credentials")

    def __register(self, node_name, img_name, target_name):
        self.logger.debug("Entered register")
        self.logger.debug("Got parameters = %s %s %s",node_name,img_name,target_name)
        self.logger.debug("Getting MAC address from HaaS for node %s",node_name)
        mac_addr = "01-" + self.haas.get_node_mac_addr(node_name).replace(":",
                                                                          "-")
        self.logger.debug("The name for pxelinux is %s",mac_addr)
        self.logger.debug("Generating ipxe file")
        self.__generate_ipxe_file(node_name, target_name)
        self.logger.debug("Finished ipxe file")
        self.logger.debug("Generating MAC addr file")
        self.__generate_mac_addr_file(img_name, node_name, mac_addr)
        self.logger.debug("Finished MAC addr file")
        self.logger.debug("Exiting register")

    def __generate_ipxe_file(self, node_name, target_name):
        self.logger.debug("Entered Generate IPXE File")
        self.logger.debug("Got Parameters = %s %s",node_name,target_name)
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        self.logger.debug("Template LOC = %s",template_loc)
        path = self.config.ipxe_loc + node_name + ".ipxe"
        self.logger.debug("The Path for ipxe file is %s",path)
        self.logger.debug("Generating ipxe file")
        with io.open(path, 'w') as ipxe:
            for line in io.open(template_loc + "/ipxe.temp", 'r'):
                line = line.replace(constants.IPXE_TARGET_NAME, target_name)
                ipxe.write(line)
        self.logger.debug("Generated ipxe file")
        self.logger.debug("Changing permissions to 755")
        os.chmod(path, 0755)
        self.logger.debug("Changed permissions to 755")
        self.logger.debug("Exiting Generate IPXE file")

    def __generate_mac_addr_file(self, img_name, node_name, mac_addr):
        self.logger.debug("Entered Generate Mac Addr File")
        self.logger.debug("Got parameters = %s %s %s",img_name,node_name, mac_addr)
        template_loc = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        self.logger.debug("Template LOC = %s",template_loc)
        path = self.config.pxelinux_loc + mac_addr
        self.logger.debug("The Path for mac addr file is %s",path)
        self.logger.info("Generating mac addr file")
        with io.open(path, 'w') as mac:
            for line in io.open(template_loc + "/mac.temp", 'r'):
                line = line.replace(constants.MAC_IMG_NAME, img_name)
                line = line.replace(constants.MAC_IPXE_NAME, node_name + ".ipxe")
                mac.write(line)
        self.logger.info("Generated mac addr file")
        self.logger.debug("Changing permissions to 644")
        os.chmod(path, 0644)
        self.logger.debug("Changed permissions to 644")

    # Calling shell script which executes a iscsi update as we don't have
    # rbd map in documentation.
    def __call_shellscript(self, *args):
        self.logger.debug("Entered call_shellscript")
        arglist = list(args)
        self.logger.debug("Got parameters = %s", arglist)
        self.logger.debug("Creating process")
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        self.logger.debug("Created Process")
        self.logger.debug("Calling Communicate")
        ret = proc.communicate()
        self.logger.debug("Got output = %s after communicate", ret)
        self.logger.debug("Exiting call_shellscript")
        return ret

    # Parses the Exception and returns the dict that should be returned to user
    def __return_error(self, ex):
        self.logger.debug("Entered return error")

        # Replaces the image name with id in error string
        def swap_id_with_name(err_str):
            self.logger.debug("Entering swap id with name")
            self.logger.debug("Got parameter %s",err_str)
            parts = err_str.split(" ")
            self.logger.info("Getting name for ceph name %s",parts[0])
            name = self.db.image.fetch_name_with_id(parts[0][parts[0].index("img")+3:])
            self.logger.info("Got name %s",name)
            if name is not None:
                parts[0] = name
            new_err_str = " ".join(parts)
            self.logger.info("New Error String is %s",err_str)
            self.logger.debug("Exiting swap id with name")
            return new_err_str

        self.logger.debug("Checking if FileSystemException")
        if FileSystemException in ex.__class__.__bases__:
            self.logger.debug("It is FileSystemException")
            ex_str = {constants.STATUS_CODE_KEY: ex.status_code,
                      constants.MESSAGE_KEY: swap_id_with_name(str(ex))}
            self.logger.info("The String to return is %s", ex_str)
            return ex_str
        ex_str = {constants.STATUS_CODE_KEY: ex.status_code,
                  constants.MESSAGE_KEY: str(ex)}
        self.logger.info("The String to return is %s", ex_str)
        return ex_str

    # A custom function which is wrapper around only success code that
    # we are creating.
    def __return_success(self,obj):
        msg_str = {constants.STATUS_CODE_KEY: 200, constants.RETURN_VALUE_KEY: obj}
        self.logger.info("The String to return is %s", msg_str)
        return msg_str

    def shutdown(self):
        self.logger.debug("Entered shutdown")
        self.logger.info("tearing down fs connection")
        self.fs.tear_down()
        self.logger.info("tore down fs connection")
        self.logger.info("Closing db connection")
        self.db.close()
        self.logger.info("closed db connection")
        self.logger.debug("Exiting shutdown")

    # Provisions from HaaS and Boots the given node with given image
    def provision(self, node_name, img_name, network, channel, nic):
        try:
            self.logger.debug("Entered Provision")
            self.logger.debug(
                "Got parameters = %s %s %s %s", node_name, img_name,
                network, channel, nic)
            self.logger.info(
                "Attaching Node %s to network %s", node_name, network)
            self.haas.attach_node_to_project_network(node_name, network,
                                                     channel, nic)
            self.logger.info("Successfully Attached Node %s to network %s",
                             node_name, network)

            self.logger.info("Inserting Clone into DB for %s",node_name)
            self.db.image.insert(node_name, self.pid, is_provision_clone=True)
            self.logger.info("Successfully Inserted into DB")
            clone_ceph_name = self.__get__ceph_image_name(node_name)
            self.logger.info("The ceph name of clone is %s",clone_ceph_name)

            ceph_img_name = self.__get__ceph_image_name(img_name)
            self.logger.info("Cloning image %s as %s", ceph_img_name, clone_ceph_name)
            self.fs.clone(ceph_img_name,constants.DEFAULT_SNAPSHOT_NAME,clone_ceph_name)
            self.logger.info("Successfully Finished Cloning image %s as %s",
                             ceph_img_name,
                             clone_ceph_name)
            ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
            self.logger.debug("Contents of ceph_config = %s",str(ceph_config))
            # Should be changed to python script
            self.logger.info("Calling ISCSI shellscript with create command")
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
            self.logger.debug("Got Message from ISCSI Script = %s",iscsi_output)
            if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                self.logger.info("The create command was executed successfully")
                self.logger.info("Lazily Registering node %s",node_name)
                self.__register(node_name, img_name, clone_ceph_name)
                self.logger.info("Registered node %s",node_name)
                return self.__return_success(True)

            elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                # Was not able to test this exception in test cases as the haas
                # call was blocking this exception
                # But it was raised during preparation of tests
                # Rare exception
                self.logger.debug("Raising Node Already In Use Exception")
                raise iscsi_exceptions.NodeAlreadyInUseException()

        except ISCSIException as e:
            # Message is being handled by custom formatter
            self.logger.exception('')
            clone_ceph_name = self.__get__ceph_image_name(node_name)
            self.logger.info("Ceph name for %s is %s",node_name,clone_ceph_name)
            self.logger.info("Removing %s",clone_ceph_name)
            self.fs.remove(clone_ceph_name)
            self.logger.info("Removed %s",clone_ceph_name)
            self.logger.info("Deleting %s from DB",node_name)
            self.db.image.delete_with_name_from_project(node_name, self.project)
            self.logger.info("Deleted %s from DB",node_name)
            time.sleep(30)
            self.logger.info("Detaching node %s",node_name)
            self.haas.detach_node_from_project_network(node_name, network,
                                                       nic)
            self.logger.info("Detached node %s",node_name)
            return self.__return_error(e)

        except FileSystemException as e:
            # Message is being handled by custom formatter
            self.logger.exception('')
            self.logger.info("Deleting %s from DB",node_name)
            self.db.image.delete_with_name_from_project(node_name, self.project)
            self.logger.info("Deleted %s from DB",node_name)
            time.sleep(30)
            self.logger.info("Detaching node %s",node_name)
            self.haas.detach_node_from_project_network(node_name, network,
                                                       nic)
            self.logger.info("Detached node %s",node_name)
            return self.__return_error(e)
        except DBException as e:
            self.logger.exception(
                '')  # Message is being handled by custom formatter
            time.sleep(30)
            self.haas.detach_node_from_project_network(node_name, network,
                                                       nic)
            return self.__return_error(e)
        except HaaSException as e:
            self.logger.exception(
                '')  # Message is being handled by custom formatter
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Provision")

    # This is for detach a node and removing it from iscsi
    # and destroying its image
    def deprovision(self, node_name, network, nic):
        try:
            self.logger.debug("Entering Detach Node")
            self.logger.debug("Got parameters = %s %s %s", node_name, network,
                              nic)

            self.logger.info("Detaching node %s from network %s", node_name,
                             network)
            self.haas.detach_node_from_project_network(node_name,
                                                       network, nic)
            self.logger.info("Successfully detached node %s from network %s",
                             node_name, network)


            ceph_img_name = self.__get__ceph_image_name(node_name)
            self.logger.info("The ceph name of clone is %s",ceph_img_name)
            self.logger.info("Deleting %s from DB",node_name)
            self.db.image.delete_with_name_from_project(node_name, self.project)
            self.logger.info("Deleted %s from DB",node_name)
            ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
            self.logger.debug("Contents of ceph+config = %s", str(ceph_config))
            self.logger.info("Calling ISCSI Shellscript with delete command")
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
            self.logger.debug("Got Message from ISCSI Script = %s",
                              iscsi_output)
            if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                self.logger.info("The delete command was executed successfully")
                self.logger.info("Removing Image %s", node_name)
                ret = self.fs.remove(str(ceph_img_name).encode("utf-8"))
                self.logger.info("Successfully Removed Image %s", node_name)
                return self.__return_success(ret)

            elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                self.logger.debug("Raising Node Already Unmapped Exception")
                raise iscsi_exceptions.NodeAlreadyUnmappedException()
        except FileSystemException as e:
            self.logger.info("Calling ISCSI Shellscript with create command")
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
            self.logger.debug("Got Message from ISCSI Script = %s",
                              iscsi_output)
            self.logger.info("Inserting %s into DB",node_name)
            self.db.image.insert(node_name, self.pid, is_provision_clone=True,
                                 id=ceph_img_name[3:])
            self.logger.info("Inserted %s into DB",node_name)
            time.sleep(30)
            self.logger.info("Attaching %s",node_name)
            self.haas.attach_node_haas_project(self.project, node_name)
            self.logger.info("Attached %s",node_name)
            return self.__return_error(e)
        except ISCSIException as e:
            self.logger.info("Inserting %s into DB",node_name)
            self.db.image.insert(node_name, self.pid, is_provision_clone=True,
                                 id=ceph_img_name[3:])
            self.logger.info("Inserted %s into DB",node_name)
            time.sleep(30)
            self.logger.info("Attaching %s",node_name)
            self.haas.attach_node_haas_project(self.project, node_name)
            self.logger.info("Attached %s",node_name)
            return self.__return_error(e)
        except DBException as e:
            self.logger.exception('')
            time.sleep(30)
            self.logger.info("Attaching %s",node_name)
            self.haas.attach_node_haas_project(self.project, node_name)
            self.logger.info("Attached %s",node_name)
            return self.__return_error(e)
        except HaaSException as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Detach Node")

    # Creates snapshot for the given image with snap_name as given name
    # fs_obj will be populated by decorator
    def create_snapshot(self, node_name, snap_name):
        try:
            self.logger.debug("Entered Create Snapshot")
            self.logger.debug("Got parameters = %s %s", node_name, snap_name)

            self.logger.info("Authenticating project %s", self.project)
            self.haas.validate_project(self.project)
            self.logger.info("Successfully Authenticated project %s",
                             self.project)

            self.logger.debug("Getting image id for image %s in project %s",
                              node_name, self.project)

            self.logger.debug("Getting ceph name for image %s in project %s",
                              node_name, self.project)
            ceph_img_name = self.__get__ceph_image_name(node_name)

            self.logger.debug("Got img_name = %s for image %s in project %s",
                              ceph_img_name, node_name, self.project)

            self.logger.info("Creating snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.fs.snap_image(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Created snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.logger.info("Protecting snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.fs.snap_protect(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Successfully Protected snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)

            self.logger.info("Inserting %s into DB",snap_name)
            self.db.image.insert(snap_name, self.pid, is_snapshot=True)
            self.logger.info("Inserted %s into DB",snap_name)

            snap_ceph_name = self.__get__ceph_image_name(snap_name)
            self.logger.info("The ceph name is %s",snap_ceph_name)
            self.logger.info("Cloning %s as %s",ceph_img_name+"@"+constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME,
                          snap_ceph_name)
            self.logger.info("Cloned %s as %s",ceph_img_name+"@"+constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.logger.info("Flattening %s",snap_ceph_name)
            self.fs.flatten(snap_ceph_name)
            self.logger.info("Flattened %s",snap_ceph_name)
            self.logger.info("Creating snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.fs.snap_image(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Created snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.logger.info("Protecting snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.fs.snap_protect(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Successfully Protected snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.logger.info("Unprotecting snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.fs.snap_unprotect(ceph_img_name,
                                   constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Successfully Unprotecting snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.logger.info("Removing snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            self.fs.remove_snapshot(ceph_img_name,
                                    constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Removed snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,snap_ceph_name)
            return self.__return_success(True)

        except (HaaSException, DBException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Create Snapshot")

    # Lists snapshot for the given image img_name
    # URL's have to be read from BMI config file
    # fs_obj will be populated by decorator
    def list_snapshots(self):
        try:
            self.logger.debug("Entered List Snapshots")
            self.logger.debug("No parameters")

            self.logger.info("Authenticating project %s", self.project)
            self.haas.validate_project(self.project)
            self.logger.info("Successfully Authenticated project %s",
                             self.project)
            self.logger.info("Fetching Snapshots for project %s",self.project)
            snapshots = self.db.image.fetch_snapshots_from_project(self.project)
            self.logger.info("Got snapshots %s",str(snapshots))
            return self.__return_success(snapshots)

        except (HaaSException, DBException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting List Snapshots")

    # Removes snapshot snap_name for the given image img_name
    # fs_obj will be populated by decorator
    def remove_image(self, img_name):
        try:
            self.logger.debug("Entered Remove Snaps")
            self.logger.debug("Got parameters = %s", img_name)

            self.logger.info("Authenticating project %s", self.project)
            self.haas.validate_project(self.project)

            self.logger.info("Successfully Authenticated project %s",
                             self.project)

            self.logger.debug("Getting ceph name for image %s in project %s",
                              img_name, self.project)
            ceph_img_name = self.__get__ceph_image_name(img_name)

            self.logger.debug("Got ceph name = %s for image %s in project %s",
                              ceph_img_name, img_name, self.project)

            self.logger.info("Unprotecting snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.fs.snap_unprotect(ceph_img_name,
                                   constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Successfully Unprotected snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.logger.info("Removing snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.fs.remove_snapshot(ceph_img_name,
                                    constants.DEFAULT_SNAPSHOT_NAME)
            self.logger.info("Removed snapshot %s for %s",constants.DEFAULT_SNAPSHOT_NAME,ceph_img_name)
            self.logger.info("Removing image %s",ceph_img_name)
            self.fs.remove(ceph_img_name)
            self.logger.info("Removed image %s",ceph_img_name)
            self.logger.info("Deleting %s from DB",img_name)
            self.db.image.delete_with_name_from_project(img_name,self.project)
            self.logger.info("Deleted %s from DB",img_name)
            return self.__return_success(True)
        except (HaaSException, DBException, FileSystemException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting Remove Snaps")

    # Lists the images for the project which includes the snapshot
    def list_images(self):
        try:

            self.logger.debug("Entered List All Images")
            self.logger.debug("Got parameters = %s", self.project)

            self.logger.info("Authenticating project %s", self.project)
            self.haas.validate_project(self.project)
            self.logger.info("Successfully Authenticated project %s",
                             self.project)

            self.logger.info("Fetching names from db for project %s",
                             self.project)
            names = self.db.image.fetch_images_from_project(self.project)
            self.logger.info("Got names successfully from db for project %s",
                             project)
            self.logger.debug("Names = %s", str(names))
            return self.__return_success(names)

        except (HaaSException, DBException) as e:
            self.logger.exception('')
            return self.__return_error(e)
        finally:
            self.logger.debug("Exiting List All Images")
