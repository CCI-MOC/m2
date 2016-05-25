#!/usr/bin/python
import ConfigParser
import subprocess

from ceph_wrapper import *
from database import *
from haas_wrapper import *


class GlobalConfig(object):
    # once we have a config file going, this object will parse the config file.
    # for the time being we are going to hard code the inits.
    def __init__(self):
        self.configfile = 'bmiconfig.cfg'
        self.fs = {}

    # add parser code here once we have a configfile/ if we decide on a Db
    # we put the db code here.
    # def __str__(self):
    #     return {'file system :': self.fstype,
    #             'rid': self.rid, 'pool': self.pool,
    #             'configfile': self.r_conf}

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read(self.configfile):
                raise IOError('cannot load ' + self.configfile)

            self.iscsi_update = config.get(constants.ISCSI_CONFIG_SECTION_NAME,
                                           constants.ISCSI_CONFIG_URL_KEY)

            self.haas_url = config.get(constants.HAAS_CONFIG_SECTION_NAME,
                                       constants.HAAS_CONFIG_URL_KEY)

            for k, v in config.items(constants.FILESYSTEM_CONFIG_SECTION_NAME):
                if v == 'True':
                    self.fs[k] = {}

                    for key, value in config.items(k):
                        self.fs[k][key] = value

                        # if self.fstype == 'ceph':
                        #     self.rid = config.get(self.fstype, 'id')
                        #     self.pool = config.get(self.fstype, 'pool')
                        #     self.r_conf = config.get(self.fstype, 'conf_file')
                        #     self.keyring = config.get(self.fstype, 'keyring')
        except ConfigParser.NoOptionError, err:  # which is same as 'exp as e'
            print str(err)


# Calling shell script which executes a iscsi update as we don't have
# rbd map in documentation.
def call_shellscript(*args):
    arglist = list(args)
    proc = subprocess.Popen(arglist, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()


def validation_decorator(func):
    def caller(*args, **kwargs):
        fs_obj = None

        try:

            usr = args[0]
            passwd = args[1]
            project = args[2]

            config = create_config()
            fs_obj = init_fs(config)

            check_auth(config.haas_url, usr, passwd, project)
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

            # Should change wrapper argument to accept int
            return return_success(
                func(*args, **kwargs))

        except (HaaSException, DBException, FileSystemException) as e:
            return return_error(e)

        finally:
            if fs_obj is not None:
                fs_obj.tear_down()

    return caller


# given. The nodes are typically implemented using ceph.

# provision : when map filename to num, create num files instead of image_name.
# given. The nodes are typically implemented using ceph.

# provision : when map filename to num, create num files instead of image_name.
def provision(usr, pwd, node_name, img_name="hadoopMaster.img",
              snap_name="HadoopMasterGoldenImage",
              network="bmi-provision"):
    fs_obj = None
    try:
        config = create_config()
        fs_obj = init_fs(config)

        attach_node_to_project_network(config.haas_url, node_name, network, usr,
                                       pwd)

        fs_obj.clone(img_name.encode('utf-8'),snap_name.encode('utf-8'),
                     node_name.encode("utf-8"))

        ceph_config = config.fs[constants.CEPH_CONFIG_SECTION_NAME]
        # Should be changed to python script
        iscsi_output = call_shellscript(config.iscsi_update,
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
            raise shellscript_exceptions.NodeAlreadyInUseException()

    except (HaaSException, ShellScriptException, FileSystemException) as e:
        return return_error(e)

    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# This is for detach a node and removing it from iscsi
# and destroying its image
def detach_node(usr, pwd, node_name, network="bmi-provision"):
    fs_obj = None
    try:

        config = create_config()
        fs_obj = init_fs(config)

        detach_node_from_project_network(config.haas_url, node_name,
                                         network, usr, pwd)

        ceph_config = config.fs[constants.CEPH_CONFIG_SECTION_NAME]

        iscsi_output = call_shellscript(config.iscsi_update,
                                        [ceph_config['keyring'],
                                         ceph_config['id'], ceph_config['pool'],
                                         node_name,
                                         constants.ISCSI_DELETE_COMMAND])
        if constants.ISCSI_UPDATE_SUCCESS in iscsi_output[0]:
            return return_success(fs_obj.remove(node_name.encode("utf-8")))
        elif constants.ISCSI_UPDATE_FAILURE in iscsi_output[0]:
            raise shellscript_exceptions.NodeAlreadyUnmappedException()
    except (HaaSException, ShellScriptException, FileSystemException) as e:
        return return_error(e)
    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# Creates snapshot for the given image with snap_name as given name
@validation_decorator
def create_snapshot(usr, passwd, project, img_name, snap_name, fs_obj=None):
    return fs_obj.snap_image(img_name, snap_name)


# Lists snapshot for the given image img_name
# URL's have to be read from BMI config file
@validation_decorator
def list_snaps(usr, passwd, project, img_name, fs_obj=None):
    return fs_obj.list_snapshots(img_name)


# Removes snapshot sna_name for the given image img_name
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


# Creates a filesystem configuration object
def create_config():
    config = GlobalConfig()
    config.parse_config()
    return config


# This function initializes files system object and
# returns an object for it.
def init_fs(config):
    try:
        if config.fs.has_key(constants.CEPH_CONFIG_SECTION_NAME):
            return RBD(config.fs[constants.CEPH_CONFIG_SECTION_NAME])
    except FileSystemException as e:
        return return_error(e)


# A custom function which is wrapper around only success code that
# we are creating.
def return_success(obj):
    return {constants.STATUS_CODE_KEY: 200, constants.RETURN_VALUE_KEY: obj}


def return_error(ex):
    parser = ExceptionParser()
    if FileSystemException in ex.__class__.__bases__:
        return {constants.STATUS_CODE_KEY: parser.parse(ex),
                constants.MESSAGE_KEY: swap_id_with_name(str(ex))}
    return {constants.STATUS_CODE_KEY: parser.parse(ex),
            constants.MESSAGE_KEY: str(ex)}


def swap_id_with_name(str):
    parts = str.split(" ")
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

    # config = GlobalConfig()
    # config.parse_config()
    # print config.fs

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
