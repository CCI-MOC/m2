#! env python
import rados
import rbd
import os


class CephBase(object):

    def __init__(self, rid, r_conf, pool, debug=None):
        if not rid or not r_conf or not pool:
            raise Exception("one or more arguments for ceph is incorrect")
        if not os.path.isfile(r_conf):
            raise Exception("invalid configuration file")

        self.rid = rid
        self.r_conf = r_conf
        self.pool = pool
        self.cluster = self.__init_cluster()
        self.ctx = self.__init_context()
        self.rbd = self.__init_rbd()
        self.is_debug = False
        self.c_img_list = list()
        if debug:   
            self.is_debug = debug
        
    
    def __repr__(self):
        return str([self.rid, self.r_conf, self.pool, self.is_debug])
#
# log in case of debug
#
    def __str__(self):
        return 'rid = {0}, conf_file = {1}, pool = {2},'\
                'is_debug? = {3}'.format(self.rid,   \
                    self.r_conf, self.pool, self.is_debug)      

    def __init_context(self):
        try:
            return  self.cluster.open_ioctx(self.\
                pool.encode('utf-8'))
        except Exception as e:
            raise e
    def __init_cluster(self):
        try:
            cluster = rados.Rados(rados_id = self.rid, conffile = self.r_conf)
            cluster.connect()
            return cluster      
        except Exception as e:
            raise e

    def __init_rbd(self):
        try:
            return rbd.RBD() 
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

    def tear_down(self):
        try:
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
                raise Exception("post image creation check failed")
        except Exception as e:
            raise e
    
    def remove(self,  iname, ctx = None):
        if not ctx:
            ctx = self.ctx
        if iname in self.c_img_list:
            self._remove(iname, ctx) 
        else:
            raise Exception("image not found in list,'\
                    ' use the unsafe remove if you are sure")
        if iname not in self.list_n():
            self.c_img_list.remove(iname)
            return True
        else:
            raise Exception("post image removal\
                    ' check failed")

    def _remove(self, iname, ctx = None):
            try:
                if not ctx:
                    ctx = self.ctx
                self.rbd.remove(ctx, iname)
            except Exception as e:
                raise e


if __name__ == "__main__" :
    a = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
    b  = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
    a.clone("hadoopMaster.img".encode('utf-8'), "HadoopMasterGoldenImage".encode('utf-8'),"ABLALdALA".encode('utf-8'))
    print a.c_img_list
    print a.list_n()
    print a.remove("ABLALdALA")
    print a.list_n()
    a.tear_down()   
