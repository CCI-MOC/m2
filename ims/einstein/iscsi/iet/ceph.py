import constants as iet_constants
import ims.common.constants as constants
import ims.common.shell as shell
import ims.exception.config_exceptions as config_exceptions
from ims.common.log import log, create_logger

logger = create_logger(__name__)


# Used by only IET
class RBD:
    def __init__(self, fs_config):
        self.__validate(fs_config)

    def __validate(self, fs_config):
        try:
            self.rid = fs_config[iet_constants.CEPH_ID_KEY]
            self.pool = fs_config[iet_constants.CEPH_POOL_KEY]
            self.keyring = fs_config[iet_constants.CEPH_KEY_RING_KEY]
        except KeyError as e:
            section = constants.FS_CONFIG_SECTION_NAME
            raise config_exceptions.MissingOptionInConfigException(str(e),
                                                                   section)

    @log
    def map(self, ceph_img_name):
        command = iet_constants.MAP_COMMAND.format(self.keyring,
                                                   self.rid,
                                                   self.pool,
                                                   ceph_img_name)
        output = shell.call(command, sudo=True)
        return output

    @log
    def unmap(self, rbd_name):
        command = iet_constants.UNMAP_COMMAND.format(self.keyring,
                                                     self.rid,
                                                     rbd_name)
        output = shell.call(command, sudo=True)
        return output

    @log
    def showmapped(self):
        output = shell.call(iet_constants.LIST_MAPPED_COMMAND)
        lines = output.split('\n')[1:-1]
        maps = {}
        for line in lines:
            parts = line.split()
            maps[parts[2]] = parts[4]
        return maps
