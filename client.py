import rados
import rbd
def connect_to_rados():
        client = rados.Rados(rados_id = "henn",conffile ="/etc/ceph/ceph.conf")
        try:
            client.connect()
            pool_to_open = "boot-disk-prototype"
            ioctx = client.open_ioctx(pool_to_open.encode('utf-8'))
            print "Connection successful"
            images = rbd.RBD().list(ioctx)
            for image in images:
                print image
            client.shutdown()
            return client, ioctx

        except rados.Error:
            # shutdown cannot raise an exception
            client.shutdown()
            raise

