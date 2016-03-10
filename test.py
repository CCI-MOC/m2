from ceph_wrapper import *
def writetoceph():
    #with open("cirros.img",'rb'):
    a = ''.join(a for str(a) in range(100))
    print a
    a = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
