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
        try:
            self.configfile = 'bmiconfig.cfg'
        except Exception, e:
            print e

    # add parser code here once we have a configfile/ if we decide on a Db
    # we put the db code here.
    def __str__(self):
        return {'file system :': self.fstype, \
                'rid': self.rid, 'pool': self.pool, \
                'configfile': self.r_conf}

    def parse_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            config.read(self.configfile)
            for k, v in config.items('filesystem'):
                if v == 'True':
                    self.fstype = k
            if self.fstype == 'ceph':
                self.rid = config.get(self.fstype, 'id')
                self.pool = config.get(self.fstype, 'pool')
                self.r_conf = config.get(self.fstype, 'conf_file')
                self.keyring = config.get(self.fstype, 'keyring')
        except ConfigParser.NoOptionError, err:  # which is same as 'exp as e'
            print str(err)


# Calling shell script which executes a iscsi update as we don't have
# rbd map in documentation.
def call_shellscript(path, m_args):
    arglist = []
    arglist.append(path)
    for arg in m_args:
        arglist.append(arg)
    proc = subprocess.Popen(arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.communicate()


# given. The nodes are typically implemented using ceph.

# provision : when map filename to num, create num files instead of image_name.
def provision(node_name, img_name="hadoopMaster.img", \
              snap_name="HadoopMasterGoldenImage", \
              debug=False):
    fs_obj = None
    try:
        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        if fs_obj.clone(img_name.encode('utf-8'), \
                        snap_name.encode('utf-8'), \
                        node_name.encode("utf-8")):
            iscsi_output = call_shellscript('./iscsi_update.sh', \
                                            [fsconfig.keyring, \
                                             fsconfig.rid, fsconfig.pool, node_name, 'create'])
            if 'successfully' in iscsi_output[0]:
                return ret_200(True)
            elif 'already' in iscsi_output[0]:
                raise shellscript_exceptions.NodeAlreadyInUseException()
    except (ShellScriptException, FileSystemException) as e:
        return return_error(e)

    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# This is for detach a node and removing it from iscsi
# and destroying its image

def detach_node(node_name):
    fs_obj = None
    try:
        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        iscsi_output = call_shellscript('./iscsi_update.sh', \
                                        [fsconfig.keyring, \
                                         fsconfig.rid, fsconfig.pool, node_name, \
                                         'delete'])
        if 'successfully' in iscsi_output[0]:
            fs_obj._remove(node_name.encode("utf-8"))
            return ret_200(True)
        elif 'already' in iscsi_output[0]:
            raise shellscript_exceptions.NodeAlreadyUnmappedException()
    except (ShellScriptException, FileSystemException) as e:
        return return_error(e)
    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# Creates snapshot for the given image with snap_name as given name
def create_snapshot(url, usr, passwd, project, img_name, snap_name):
    fs_obj = None

    try:
        check_auth(url, usr, passwd, project)

        pr = ProjectRepository()
        pid = pr.fetch_id_with_name(project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            raise db_exceptions.ProjectNotFoundException(project)
        imgr = ImageRepository()
        img_id = imgr.fetch_id_with_name_from_project(img_name, project)
        if img_id is None:
            raise db_exceptions.ImageNotFoundException(img_name)

        fs_config = create_fsconfigobj()
        fs_obj = init_fs(fs_config)

        # Should change wrapper argument to accept int
        return ret_200(fs_obj.snap_image(str(img_id), snap_name))
    except (HaaSException, DBException, FileSystemException) as e:
        return return_error(e)
    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# Lists snapshot for the given image img_name
# URL's have to be read from BMI config file
def list_snaps(url, usr, passwd, project, img_name):
    fs_obj = None
    try:
        check_auth(url, usr, passwd, project)
        pr = ProjectRepository()
        pid = pr.fetch_id_with_name(project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            raise db_exceptions.ProjectNotFoundException(project)
        imgr = ImageRepository()
        img_id = imgr.fetch_id_with_name_from_project(img_name, project)

        if img_id is None:
            raise db_exceptions.ImageNotFoundException(img_name)

        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        return ret_200(fs_obj.list_snapshots(str(img_id)))

    except (HaaSException, DBException, FileSystemException) as e:
        return return_error(e)
    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# Removes snapshot sna_name for the given image img_name
def remove_snaps(url, usr, passwd, project, img_name, snap_name):
    fs_obj = None
    try:
        check_auth(url, usr, passwd, project)

        pr = ProjectRepository()
        pid = pr.fetch_id_with_name(project)
        # None as a query result implies that the project does not exist.
        if pid is None:
            raise db_exceptions.ProjectNotFoundException(project)
        imgr = ImageRepository()
        img_id = imgr.fetch_id_with_name_from_project(img_name, project)

        if img_id is None:
            raise db_exceptions.ImageNotFoundException(img_name)

        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        return ret_200(fs_obj.remove_snapshots(str(img_id), snap_name))
    except (HaaSException, DBException, FileSystemException) as e:
        return return_error(e)
    finally:
        if fs_obj is not None:
            fs_obj.tear_down()


# Lists the images for the project which includes the snapshot
def list_all_images(url, usr, passwd, project):
    try:
        check_auth(url, usr, passwd, project)
        imgr = ImageRepository()
        return imgr.fetch_names_from_project(project)
    except (HaaSException, DBException) as e:
        return return_error(e)


# Creates a filesystem configuration object
def create_fsconfigobj():
    fsconfig = GlobalConfig()
    fsconfig.parse_config()
    return fsconfig


# This function initializes files system object and
# returns an object for it.
def init_fs(fsconfig, debug=False):
    try:
        if fsconfig.fstype == "ceph":
            return RBD(fsconfig.rid, \
                       fsconfig.r_conf, \
                       fsconfig.pool, debug)
    except FileSystemException as e:
        return return_error(e)


# A custom function which is wrapper around only success code that
# we are creating.
def ret_200(obj):
    return {"status_code": 200, "retval": obj}


def return_error(ex):
    parser = ExceptionParser()
    return {"status_code": parser.parse(ex), "msg": str(ex)}


if __name__ == "__main__":
    print check_auth('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate')
    print list_all_images('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'test')
    print list_all_images('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate')
    print list_snaps('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate', 'testimage')
    # print create_snapshot('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate','testimage', 'blblb1')
    print remove_snaps('http://127.0.0.1:6500/', "haasadmin", "admin1234", 'bmi_penultimate', 'testimage', 'blblb1')
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
