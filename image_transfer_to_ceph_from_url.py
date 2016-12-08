from ceph_wrapper import *
import requests
'''
class g_data(object):
    def __init__(self, block_sz = (1024*1024))
        self.block_sz = block_sz

def DownloadFromURL(url):
    req = requests.get(url, stream = True)
'''            
def write_to_ceph(url):
    #image = open("cirros.img")
    #image.read() 
    #print a
    req = requests.get(url, stream = True)
    #file = "cirros.img"
    a = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
    #order = int(math.log(self.WRITE_CHUNKSIZE, 2))
    #print a.rbd.get_fsid()
    a.create_image("centos_test1.img", "centos_test1.img",1048576)
    #gdata = g_data()
    #a.img_dict("cirros1.img")
    a.init_image("centos_test1.img")
    with a.img_dict["centos_test1.img"] as image:
        print image.stripe_count()
        print image.stat()
        print image.size()
        bytes_written = 0
        offset = 0
        for chunk in req.iter_content(chunk_size =1024 * 1024):    
                byte = chunk
                if not byte:
                    break
                else:
                    chunk_length = len(byte)
                    length = offset + chunk_length
                    bytes_written += chunk_length
                    image.resize(length)
                    offset += image.write(byte, offset)
    a.tear_down()    

if __name__ == "__main__":
    write_to_ceph("http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1503.qcow2")
