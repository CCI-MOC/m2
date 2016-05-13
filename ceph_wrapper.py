#! /bin/python
import os

import rados
import rbd
from exception import *


# Need to define abstract class for Filesystem in a seperate file.


class CephBase(object):
    def __init__(self, rid, r_conf, pool, debug=None):
        if not rid or not r_conf or not pool:
            raise file_system_exceptions.IncorrectConfigArgumentException()
        if not os.path.isfile(r_conf):
            raise file_system_exceptions.InvalidConfigFileException()
        self.rid = rid
        self.r_conf = r_conf
        self.pool = pool
        self.cluster = self.__init_cluster()
        self.ctx = self.__init_context()
        self.rbd = self.__init_rbd()
        self.is_debug = False
        if debug:
            self.is_debug = debug

    def __repr__(self):
        return str([self.rid, self.r_conf, self.pool, self.is_debug])

    #
    # log in case of debug
    #
    def __str__(self):
        return 'rid = {0}, conf_file = {1}, pool = {2},' \
               'is_debug? = {3}, current images {4}' \
            .format(self.rid, self.r_conf, \
                    self.pool, self.is_debug)

    def __init_context(self):
        return self.cluster.open_ioctx(self.pool.encode('utf-8'))

    def __init_cluster(self):
        cluster = rados.Rados(rados_id=self.rid, conffile=self.r_conf)
        cluster.connect()
        return cluster

    def __init_rbd(self):
        return rbd.RBD()

    def init_image(self, name, ctx=None, snapshot=None, read_only=False):
        try:
            if not ctx:
                ctx = self.ctx
            image_instance = rbd.Image(ctx, name, snapshot, read_only)
            ##return True We return True because we can already reference the image
            ##using the name as the key to the dict. The worklflos is something like
            return image_instance
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
        return self.rbd.list(self.ctx)

    def clone(self, p_name, p_snap, c_nm,p_ctx=None, c_ctx=None):
        try:
            if not p_ctx:
                p_ctx = self.ctx
            if not c_ctx:
                c_ctx = self.ctx
            self.rbd.clone(p_ctx, p_name, p_snap, c_ctx, c_nm, features=1)
            return True
        except rbd.ImageExists() as e:
            raise file_system_exceptions.ImageExistsException()
        except rbd.FunctionNotSupported as e:
            raise file_system_exceptions.FunctionNotSupportedException()
        except rbd.ArgumentOutOfRange as e:
            raise file_system_exceptions.ArgumentsOutOfRangeException()

    def remove(self, iname, ctx=None):
        try:
            if not ctx:
                ctx = self.ctx
            self._remove(iname, ctx)
            return True
        except rbd.ImageNotFound as e:
            raise file_system_exceptions.ImageNotFoundException()
        except rbd.ImageBusy as e:
            raise file_system_exceptions.ImageBusyException()
        except rbd.ImageHasSnapshots as e:
            raise file_system_exceptions.ImageHasSnapshotException()

    def _remove(self, iname, ctx=None):
        if not ctx:
            ctx = self.ctx
        self.rbd.remove(ctx, iname)

    def write(self, img_id, data, offset):
        try:
            img = self.init_image(name=img_id)
            img.write(data, offset)
            img.close()
        except KeyError as e:
            raise file_system_exceptions.ImageNotOpenedException()

    def snap_image(self, img_id, name):
        try:
            img = self.init_image(name=img_id)
            img.create_snap(name)
            img.close()
            return True
        except KeyError as e:
            raise file_system_exceptions.ImageNotOpenedException()
        except rbd.ImageExists as e:
            raise file_system_exceptions.ImageExistsException()

    def list_snapshots(self, img_id):
        try:
            img = self.init_image(img_id)
            snap_list_iter = img.list_snaps()
            snap_list = [snap['name'] for snap in snap_list_iter]
            return snap_list
        except KeyError as e:
            raise file_system_exceptions.ImageNotOpenedException()

    def remove_snapshots(self, img_id, name):
        try:
            img = self.init_image(name=img_id)
            img.remove_snap(name)
            img.close()
            return True
        except KeyError as e:
            raise file_system_exceptions.ImageNotOpenedException()
        except rbd.ImageBusy as e:
            raise file_system_exceptions.ImageBusyException()

    def create_image(self, img_id, img_size, ctx=None):
        try:
            ctx = self.ctx
            self.rbd.create(ctx, img_id, img_size)
            return True
        except rbd.ImageExists as e:
            raise file_system_exceptions.ImageExistsException()
        except rbd.FunctionNotSupported as e:
            raise file_system_exceptions.FunctionNotSupportedException()

    def get_image(self, img_id):
        """
           Gets image object for manipulation
        """
        try:
            return self.init_image(img_id)
        except KeyError as e:
            raise file_system_exceptions.ImageNotOpenedException()
