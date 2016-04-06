#!/usr/bin/python
import sys
from ceph_wrapper import *
import ConfigParser, os
import subprocess

class GlobalConfig(object):
    # once we have a config file going, this object will parse the config file.
    # for the time being we are going to hard code the inits.
        
    def __init__(self):
        self.configfile = 'bmiconfig.cfg'
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
        #print arglist
        #print "the above is the cmdline that will run on the current machine"
        for arg in m_args:
                print arg
                arglist.append(arg)
        #print "created argslist" + str(arglist)
        proc = subprocess.Popen(arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.communicate()

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
                              } # throw 401 ... ?(not yet decided) these are placeholders for now, will work though 
        self.current_err = self.exception_dict[type(e)]

    def parse_curr_err(self, emsg = "Generic Error"):
        if self.exception.message:
            emsg = self.exception.message
        return {'status_code' : self.current_err, 'msg' : emsg}


def provision(fs_obj, node_name, img_name = "hadoopMaster.img",\
        snap_name = "HadoopMasterGoldenImage",\
        debug = False):
    
#   '''Provisioning the nodes for a given project using the image and snapshot name
#        given. The nodes are typically implemented using ceph.'''
          
    try:
        if fs_obj.clone(img_name.encode('utf-8'),\
                snap_name.encode('utf-8'),\
                node_name.encode("utf-8")):
            #call_shellscript('ls', [fs_obj.keyring, \
            #                    fs_obj.rid, fs_obj.pool, node_name])
            return  ret_200(True)

    except Exception as e:
        return ResponseException(e).parse_curr_err() 
#This is for detach a node and removing it from iscsi
#and destroying its image
def detach_node(node_name):
    try:
        fsconfig = GlobalConfig()
        fsconfig.parse_config()
        fs_obj = init_fs(fsconfig)
        iscsi_output = call_shellscript('/home/user/ims/iscsi_update.sh', \
                                        [fsconfig.keyring, \
                                fsconfig.rid, fsconfig.pool, node_name,\
                                'delete'])
        if 'successfully' in iscsi_output[0]:
            output = remove(fs_obj, node_name)
            if output:
                return True
        elif 'already' in iscsi_output[0]:
            return "Node already part unmapped and no image exists"
        else:
            return False
    finally:
            fs_obj.tear_down()
            


def remove(fs_obj, node_name):
    
#        '''Removes the image from given project '''
     
    try:
        if fs_obj._remove(node_name.encode("utf-8")):
            return ret_200(True)
    except Exception as e:
        return ResponseException(e).parse_curr_err() 

def create_snapshot(fs_obj, img_name, snap_name):
    
#      '''  Creates snapshot for the given image with snap_name as given name '''
    try:
        if fs_obj.init_image(img_name):
            return ret_200(fs_obj.snap_image(img_name, snap_name))

    except Exception as e:
         return ResponseException(e).parse_curr_err()

def map_node(node_name, img_name = "hadoopMaster.img",\
        snap_name = "HadoopMasterGoldenImage",\
        debug = False):
    try:
        fsconfig = GlobalConfig()
        fsconfig.parse_config()
        fs_obj = init_fs(fsconfig)
        if provision(fs_obj, node_name, img_name, snap_name, debug):
            iscsi_output = call_shellscript('/home/user/ims/iscsi_update.sh', \
                                        [fsconfig.keyring, \
                                fsconfig.rid, fsconfig.pool, node_name, 'create'])
            if 'successfully' in iscsi_output[0]:
                return True #Need to modify all return values  to have a consistent 
                        #True or False methods
            elif 'already' in iscsi_output[0]:
                return "Node is already in use"
            else:
                return False 
    finally:
            fs_obj.tear_down()   

def list_images(fs_obj, debug = True):

#'''Lists the images for the project which includes the snapshot'''
    
    try:
        return ret_200(fs_obj.list_n())

    except Exception as e:
        return ResponseException(e).parse_curr_err()

def init_fs(fsconfig, debug = False):
    try:
        if fsconfig.fstype == "ceph":
             return RBD(fsconfig.rid,\
                    fsconfig.r_conf,\
                    fsconfig.pool, debug)
           
    except Exception as e:
        return ResponseException(e).parse_curr_err()


def ret_200(obj):
    return {"status_code" : 200, "retval" : obj}
   
if __name__ == "__main__":
    #print   list_free_nodes('http://127.0.0.1:7000/', debug = True)
    #haas_ret =  query_project_nodes('http://127.0.0.1:7000/', 'bmi_infra', debug = True)
    #tt = list()
    #for jj in haas_ret.json:
    #    tt.append((jj, 'enp130s0f0'))
    #print tt
    
    fsconfig = GlobalConfig() # for now this is just hardcoded strings .  TODO, remove the comment once config files are done
    fsconfig.parse_config()
    fs_obj = init_fs(fsconfig) 
    #print fs_obj
 
    if 'create' in sys.argv:
        #ceph_obj = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug = True)
        #cb = create_bigdata_env('http://127.0.0.1:7000/', 'bmi_infra', 2, "bmi-provision", ceph_obj, debug = True)
        #ceph_obj.tear_down()
        print map_node('cisco-08',debug = True)
    if 'del' in sys.argv:
        print detach_node('cisco-08')
    if 'attach' in sys.argv:
        print add_to_project('http://127.0.0.1:7000/', 'bmi_infra', 2, "bmi-provision", debug = True)
    if 'snap' in sys.argv:
        print create_snapshot(fs_obj, "test.img", "test_snap")
    if 'ls' in sys.argv:
        print list(fs_obj)
    #node_list = query_project_nodes('http://127.0.0.1:7000/', 'bmi_infra', debug = True)
    #print node_list.json
    #print "above is nodelsit"
    #node_power_cycle('http://127.0.0.1:7000/','cisco-36', debug = True)
    #ceph_obj =  RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
    if 'detach' in sys.argv:
        ceph_obj = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug = True)
        ay = del_nodelist('http://127.0.0.1:7000/', 'bmi_infra','bmi-provision', node_list, ceph_obj, debug = True)
        ceph_obj.tear_down()
    #for kk in ay:
    #    print ay
    #fs_obj.tear_down()
    print "imin"
    try: 
        print "iminini"
        raise CephException("hello")
    except Exception as e:
        print ResponseException(e).parse_curr_err()
        
#time.sleep(5)
    #print  ax
    print "############################################# CLEARED ##########################"
