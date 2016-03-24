#! /bin/python
import rados
import rbd
import os

#Need to define abstract class for Filesystem in a seperate file. 


class CephException(Exception):
    def __init__(self, message = None, errors = None):
        super(CephException, self).__init__(message)
        self.errors = errors   
 
class CephBase(object):
    def __init__(self, rid, r_conf, pool, debug=None):
        if not rid or not r_conf or not pool:
            raise CephException("one or more arguments for ceph is incorrect")
        if not os.path.isfile(r_conf):
            raise CephException("invalid configuration file")
        self.rid = rid
        self.r_conf = r_conf
        self.pool = pool
        self.cluster = self.__init_cluster()
        self.ctx = self.__init_context()
        self.rbd = self.__init_rbd()
        self.is_debug = False
        self.c_img_list = list()
        self.img_dict = dict()
        if debug:   
            self.is_debug = debug
        
    def __repr__(self):
        return str([self.rid, self.r_conf, self.pool, self.is_debug])
#
# log in case of debug
#
    def __str__(self):
        return 'rid = {0}, conf_file = {1}, pool = {2},'\
                'is_debug? = {3}, current images {4}'\
                .format(self.rid,self.r_conf,\
                        self.pool, self.is_debug,\
                        str(self.img_dict.keys()))

    def __init_context(self):
        try:
            return  self.cluster.open_ioctx(self.\
                pool.encode('utf-8'))
        except Exception as e:
            raise e

    def __init_cluster(self):
        try:
            cluster = rados.Rados(rados_id = self.rid,\
                    conffile = self.r_conf)
            cluster.connect()
            return cluster      
        except Exception as e:
            raise e

    def __init_rbd(self):
        try:
            return rbd.RBD() 
        except Exception as e:
            raise e

    def init_image(self, name, ctx = None, \
            snapshot = None, read_only = False):
        try:
            if not ctx:
                ctx = self.ctx
            image_instance = rbd.Image(ctx, name, snapshot, read_only)
            self.img_dict[name] = image_instance 
            ##return True We return True because you can already reference the image
            ##using the name as the key to the dict. The worklflos is something like
            return True
        except Exception as e:
            raise e
# define this function in the derivative class
# to be specific for the call.

    def run(self):
        pass

# this is the teardown section, we undo things here
    def __td_context(self):
        self.ctx.close()    

    def __td_cluster(self):
        self.cluster.shutdown()
    
    def __td_images(self):
        if self.img_dict is None:
            return
        for key in self.img_dict.keys():
            self.img_dict[key].close()
            del(self.img_dict[key])

    def tear_down(self):
        try:
            self.__td_images()
            self.__td_context()
            self.__td_cluster()
        except Exception as e:
            raise e



class RBD(CephBase):
    def list_n(self):
        try:
            return self.rbd.list(self.ctx)
        except Exception as e:
            raise e
          
    def clone(self, p_name, p_snap, c_nm,\
            p_ctx = None, c_ctx = None):
        try:
            if not p_ctx:
                p_ctx = self.ctx
            if not c_ctx:
                c_ctx = self.ctx
            self.rbd.clone(p_ctx, p_name, p_snap, c_ctx,\
                    c_nm, features = 1 )
            if c_nm in self.list_n():
                self.c_img_list.append(c_nm)
                return True
            else:
                raise CephException("post image creation check failed")
        except Exception as e:
            raise e
    
    def remove(self, iname, ctx = None):
        if not ctx:
            ctx = self.ctx
        if iname in self.c_img_list:
            self._remove(iname, ctx) 
        else:
            raise CephException("image not found in list,'\
                    ' use the unsafe remove if you are sure")
        if iname not in self.list_n():
            self.c_img_list.remove(iname)
            return True
        else:
            raise CephException("post image removal\
                    ' check failed")

    def _remove(self, iname, ctx = None):
            try:
                if not ctx:
                    ctx = self.ctx
                self.rbd.remove(ctx, iname)
            except CephException as e:
                raise e

    def write(img_name, data, offset):
        try:
            if not img_name in self.img_dict:
                raise CephException('open the image first')
        self.img_dict[name].write(data, offset)
        except Exception as e:
            raise e

    def close_image(name):
        if name in self.img_dict:
            self.img_dict[name].close()
            del(self.img_dict[name])
        else:
            raise CephException("{0} not found!".format(name))

    def snap_image(self, img_name, name):
        try:
            if img_name not in self.img_dict:
                raise CephException("Invalid image name"\
                        " or image not instantiated")
            self.img_dict[img_name].create_snap(name)
            return True
        except Exception as e:
            raise e

    def create_image(self, img_name, img_file,\
                 img_size, ctx = None):
        ctx = self.ctx    
        self.rbd.create(ctx, img_name, img_size)
        return True
    
    def get_image(self, img_name):
         '''
            Gets image object for manipulation
         '''
         return self.img_dict[img_name]
        
if __name__ == "__main__" :
    pass
#    a = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
#    b  = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
#    #a.clone("hadoopMaster.img".encode('utf-8'), "HadoopMasterGoldenImage".encode('utf-8'),"ABLALdALA".encode('utf-8'))
#    a.init_image("test.img")
#    a.snap_image("test.img", "test_snap")
#    print a.c_img_list
#    print a.list_n()
#    #print a.remove("ABLALdALA")
#    print a.list_n()
#    print a
#    a.tear_down()
#    print a   
