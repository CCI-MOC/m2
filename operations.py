#!/usr/bin/python
import sys
from ceph_wrapper import *
import ConfigParser, os
import subprocess
import os.path

#As of now a shell script that can accomodate rbd map and update.
#Since there are no python rbd map and updates wrappers around ceph.
class ShellScriptException(Exception): 
    def __init__(self, message = None, errors = None):
        super(ShellScriptException, self).__init__(message)
        self.errors = errors   
 
class GlobalConfig(object):
    # once we have a config file going, this object will parse the config file.
    # for the time being we are going to hard code the inits.
        
    def __init__(self):
        try:
            self.configfile = 'bmiconfig.cfg'
        except Exception, e:
            print e
    #add parser code here once we have a configfile/ if we decide on a Db
    # we put the db code here.
    def __str__(self):
        return {'file system :' : self.fstype, \
            'rid' : self.rid, 'pool' : self.pool,\
                'configfile' : self.r_conf} 

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
        except ConfigParser.NoOptionError, err: #which is same as 'exp as e'
            print str(err)

#Calling shell script which executes a iscsi update as we don't have 
#rbd map in documentation.
def call_shellscript(path, m_args):
        arglist = []
        arglist.append(path)
        for arg in m_args:
                arglist.append(arg)
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.communicate()

#Custom Exception Class that we are going to use which is a wrapper around
#Ceph exception classes.
class ResponseException(object):
    def __init__(self, e):
        self.exception_dict = dict()
        self.exception = e
# Extend this dict as needed for future expceptions. this
# ensures readeability and uniformity of errors.
        self.exception_dict = {
           type(rbd.ImageExists())  : 401,
           type(CephException()) : 403,
           type(rbd.ImageBusy()) : 409,
           type(rbd.ImageHasSnapshots()) : 405,
           type(rbd.ImageNotFound()) : 404,
           type(rbd.FunctionNotSupported()) : 410,
           type(rbd.ArgumentOutOfRange()) : 411,
           type(ShellScriptException()) : 440,
                                }
        #This is to handle key error exception, this also gives us the default error
        self.current_err = self.exception_dict.get(type(e), 500)

    def parse_curr_err(self, debug = False):
        if self.current_err != 500:  #check for existing error code in the exception, 
            emsg = self.exception.message
        elif self.current_err == 500:
            #This is for debugging original exceptions, if we don't have this, 
            #we will always get internal error, so that end-user can't 
            #see original exceptions
            if debug == True:
                print e
            emsg = "Internal server error"
        return {'status_code' : self.current_err, 'msg' : emsg}


#Provisioning the nodes for a given project using the image and snapshot name
#given. The nodes are typically implemented using ceph.
def provision(node_name, img_name = "hadoopMaster.img",\
        snap_name = "HadoopMasterGoldenImage",\
        debug = False):
    try:
        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        if fs_obj.clone(img_name.encode('utf-8'),\
                snap_name.encode('utf-8'),\
                node_name.encode("utf-8")):
            iscsi_output = call_shellscript('iscsi_update.sh', \
                                        [fsconfig.keyring, \
                                fsconfig.rid, fsconfig.pool, node_name, 'create'])
            if 'successfully' in iscsi_output[0]:
                return ret_200(True)    
            elif 'already' in iscsi_output[0]:
                raise ShellScriptException("Node is already in use")
    except Exception as e:
        return ResponseException(e).parse_curr_err()            
    finally:
        fs_obj.tear_down()

#This is for detach a node and removing it from iscsi
#and destroying its image
def detach_node(node_name):
    try:
        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        iscsi_output = call_shellscript('iscsi_update.sh', \
                                        [fsconfig.keyring, \
                                fsconfig.rid, fsconfig.pool, node_name,\
                                'delete'])
        if 'successfully' in iscsi_output[0]:
            fs_obj._remove(node_name.encode("utf-8"))
            return ret_200(True)
        elif 'already' in iscsi_output[0]:
            raise ShellScriptException("Node already part unmapped and no image exists")
    except Exception as e:
        return ResponseException(e).parse_curr_err() 
    finally:
        fs_obj.tear_down()    


#Creates snapshot for the given image with snap_name as given name
def create_snapshot(img_name, snap_name):
    try:
        fsconfig = create_fsconfigobj() 
        fs_obj = init_fs(fsconfig)
        if fs_obj.init_image(img_name):
            a = ret_200(fs_obj.snap_image(img_name, snap_name))
            fs_obj.tear_down()
            return a

    except Exception as e:
        fs_obj.tear_down()
        return ResponseException(e).parse_curr_err()

#Lists the images for the project which includes the snapshot
def list_all_images(debug = True):
    
    try:
        fsconfig = create_fsconfigobj()
        fs_obj = init_fs(fsconfig)
        a = ret_200(fs_obj.list_n())
        fs_obj.tear_down()
        return a

    except Exception as e:
        return ResponseException(e).parse_curr_err()

#Creates a filesystem configuration object
def create_fsconfigobj():
    fsconfig = GlobalConfig()
    fsconfig.parse_config()    
    return fsconfig


#This function initializes files system object and 
# returns an object for it.
def init_fs(fsconfig, debug = False):
    try:
        if fsconfig.fstype == "ceph":
             return RBD(fsconfig.rid,\
                    fsconfig.r_conf,\
                    fsconfig.pool, debug)
           
    except Exception as e:
        return ResponseException(e).parse_curr_err()


#A custom function which is wrapper around only success code that
#we are creating.
def ret_200(obj):
    return {"status_code" : 200, "retval" : obj}
   
