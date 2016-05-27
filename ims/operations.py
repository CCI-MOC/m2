#!/usr/bin/python
import subprocess

from ceph_wrapper import *
from config import BMIConfig
from database import *
from haas_wrapper import *


# logging will be submitted later


# Decorator for snapshot methods
def validation_decorator(func):
    def caller(*args, **kwargs):
        fs_obj = None

        try:

            usr = args[0]
            pwd = args[1]
            project = args[2]

            config = create_config()
            fs_obj = init_fs(config)

            check_auth(config.haas_url, usr, pwd, project)
            img_name = args[3]

            pr = ProjectRepository()
            pid = pr.fetch_id_with_name(project)
            # None as a query result implies that the project does not exist.
            if pid is None:
                raise db_exceptions.ProjectNotFoundException(project)
            imgr = ImageRepository()
            img_id = imgr.fetch_id_with_name_from_project(img_name,
                                                          project)
            if img_id is None:
                raise db_exceptions.ImageNotFoundException(img_name)

            args = list(args)
            args[3] = str(img_id)
            args = tuple(args)

            kwargs['fs_obj'] = fs_obj

            return return_success(
                func(*args, **kwargs))

        except (HaaSException, DBException, FileSystemException) as e:
            return return_error(e)
        except ConfigException:  # Should be logged
            pass

        finally:
            if fs_obj is not None:
                fs_obj.tear_down()

    return caller


# Calling shell script which executes a iscsi update as we don't have
# rbd map in documentation.
def call_shellscript(*args):
    arglist = list(args)
    proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()


class BMI:

    def __init__(self, usr, passwd):
        self.config = create_config()
        self.haas = HaaS(base_url=self.config.haas_url, usr=usr, passwd=passwd)

    # Provisions from HaaS and Boots the given node with given image
    def provision(self,node_name, img_name="hadoopMaster.img",
                  snap_name="HadoopMasterGoldenImage",
                  network="bmi-provision"):
        try:
            self.haas.attach_node_to_project_network(node_name, network)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                fs.clone(img_name.encode('utf-8'), snap_name.encode('utf-8'),
                         node_name.encode("utf-8"))

                ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]
                # Should be changed to python script
                iscsi_output = call_shellscript(self.config.iscsi_update,
                                            [ceph_config['keyring'],
                                             ceph_config['id'],
                                             ceph_config['pool'],
                                             node_name,
                                             constants.ISCSI_CREATE_COMMAND])
                if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                    return return_success(True)
                elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                    # Was not able to test this exception in test cases as the haas
                    # call was blocking this exception
                    # But it was raised during preparation of tests
                    # Rare exception
                    raise iscsi_exceptions.NodeAlreadyInUseException()

        except (HaaSException, ISCSIException, FileSystemException) as e:
            return return_error(e)


    # This is for detach a node and removing it from iscsi
    # and destroying its image
    def detach_node(self,node_name, network="bmi-provision"):
        try:

            self.haas.detach_node_from_project_network(node_name,
                                             network)

            with RBD(self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
                ceph_config = self.config.fs[constants.CEPH_CONFIG_SECTION_NAME]

                iscsi_output = call_shellscript(self.config.iscsi_update,
                                            [ceph_config['keyring'],
                                             ceph_config['id'], ceph_config['pool'],
                                             node_name,
                                             constants.ISCSI_DELETE_COMMAND])
                if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
                    return return_success(fs.remove(node_name.encode("utf-8")))
                elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
                    raise iscsi_exceptions.NodeAlreadyUnmappedException()
        except (HaaSException, ISCSIException, FileSystemException) as e:
            return return_error(e)


# Creates snapshot for the given image with snap_name as given name
# fs_obj will be populated by decorator
@validation_decorator
def create_snapshot(usr, passwd, project, img_name, snap_name, fs_obj=None):
    return fs_obj.snap_image(img_name, snap_name)


# Lists snapshot for the given image img_name
# URL's have to be read from BMI config file
# fs_obj will be populated by decorator
@validation_decorator
def list_snaps(usr, passwd, project, img_name, fs_obj=None):
    return fs_obj.list_snapshots(img_name)


# Removes snapshot snap_name for the given image img_name
# fs_obj will be populated by decorator
@validation_decorator
def remove_snaps(usr, passwd, project, img_name, snap_name, fs_obj=None):
    return fs_obj.remove_snapshots(img_name, snap_name)


# Lists the images for the project which includes the snapshot
def list_all_images(usr, passwd, project):
    try:
        config = create_config()

        check_auth(config.haas_url, usr, passwd, project)

        pr = ProjectRepository()
        pid = pr.fetch_id_with_name(project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            raise db_exceptions.ProjectNotFoundException(project)

        imgr = ImageRepository()
        return return_success(imgr.fetch_names_from_project(project))
    except (HaaSException, DBException) as e:
        return return_error(e)
    except ConfigException:  # Should be logged
        pass


# Creates a filesystem configuration object
def create_config():
    try:
        config = BMIConfig()
        config.parse_config()
        return config
    except ConfigException:  # Should be logged
        raise  # Crashing it for now


# This function initializes files system object and
# returns an object for it.
def init_fs(config):
    try:
        # Should be made generic to remove specific dependency on FS
        if constants.CEPH_CONFIG_SECTION_NAME in config.fs:
            return RBD(config.fs[constants.CEPH_CONFIG_SECTION_NAME])
    except FileSystemException as e:
        return return_error(e)


# A custom function which is wrapper around only success code that
# we are creating.
def return_success(obj):
    return {constants.STATUS_CODE_KEY: 200, constants.RETURN_VALUE_KEY: obj}


# Parses the Exception and returns the dict that should be returned to user
def return_error(ex):
    ex_parser = ExceptionParser()
    if FileSystemException in ex.__class__.__bases__:
        return {constants.STATUS_CODE_KEY: ex_parser.parse(ex),
                constants.MESSAGE_KEY: swap_id_with_name(str(ex))}
    return {constants.STATUS_CODE_KEY: ex_parser.parse(ex),
            constants.MESSAGE_KEY: str(ex)}


# Replaces the image name with id in error string
def swap_id_with_name(err_str):
    parts = err_str.split(" ")
    imgr = ImageRepository()
    name = imgr.fetch_name_with_id(parts[0].strip())
    if name is not None:
        parts[0] = name
    return " ".join(parts)


if __name__ == "__main__":
    # print check_auth('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmipenultimate')
    # print list_all_images('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'test')
    # print list_all_images('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmipenultimate')
    # print provision("http://127.0.0.1:6500/", "haasadmin", "admin1234",
    #                 "super-37")
    # print detach_node("http://127.0.0.1:6500/", "haasadmin", "admin1234", "super-37")
    # print list_snaps('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate', 'testimage')
    # print create_snapshot('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate','testimage', 'blblb1')
    # print remove_snaps('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate', 'testimage', 'blblb1')
    '''
    print list_free_nodes('http://127.0.0.1:6500/', "haasadmin", "admin1234",  debug = True)['retval']
    time.sleep(5)

    print attach_node_haas_project('http://127.0.0.1:6500/', "bmi_penultimate", 'sun-12',\
            usr = "haasadmin", passwd = "admin1234", debug = True)
    print "above is attach node to a proj"

    print query_project_nodes('http://127.0.0.1:6500/',  "bmi_penultimate", "haasadmin", "admin1234")
    time.sleep(5)

    print attach_node_to_project_network('http://127.0.0.1:7000/', 'cisco-27',\
            "enp130s0f0", "bmi-provision","test", "test",  debug = True)
    time.sleep(5)
    print "above is attach network"

    print detach_node_from_project_network('http://127.0.0.1:7000/','cisco-27',\
            'bmi-provision', "test", "test", "enp130s0f0", debug = True)
    time.sleep(5)


    print "above is detach from net"
    print detach_node_from_project('http://127.0.0.1:6500/',\
              "bmi_penultimate", 'sun-12',  usr = "haasadmin", passwd = "admin1234",  debug = True)
    time.sleep(5)
    print "above is detach from the proj"
    print query_project_nodes('http://127.0.0.1:6500/', "bmi_penultimate", "haasadmin", "admin1234")
    time.sleep(5)
    try:
        raise ShellScriptException("lljl")
    except Exception as e:
        print ResponseException(e).parse_curr_err()
    '''
