from ims.common.log import log, create_logger

logger = create_logger(__name__)


# Used by only IET
@log
def map(self, ceph_img_name):
    command = "rbd --keyring {1} --id {2} map {3}/{4}".format(self.keyring,
                                                              self.rid,
                                                              self.pool,
                                                              ceph_img_name)
    p = subprocess.Popen(command, shell=True,
                         stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, err = p.communicate()
    # output = sh.rbd.map(ceph_img_name, keyring=self.keyring, id=self.rid,
    #            pool=self.pool)
    if p.returncode == 0:
        if output.find("sudo") != -1:
            return output.split(":")[1].strip()
        else:
            return output.strip()
    else:
        raise file_system_exceptions.MapFailedException(ceph_img_name)


@log
def unmap(self, rbd_name):
    command = "echo {0} | sudo -S rbd --keyring {1} --id {2} unmap " \
              "{3}".format(self.password, self.keyring, self.rid, rbd_name)
    p = subprocess.Popen(command, shell=True,
                         stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, err = p.communicate()
    # output = sh.rbd.unmap(rbd_name, keyring=self.keyring, id=self.rid)
    if p.returncode == 0:
        return output.strip()
    else:
        raise file_system_exceptions.UnmapFailedException(rbd_name)


@log
def showmapped(self):
    output = sh.rbd.showmapped()
    if output.exit_code == 0:
        lines = output.split('\n')[1:-1]
        maps = {}
        for line in lines:
            parts = line.split()
            maps[parts[2]] = parts[4]
        return maps
    else:
        pass
