import constants as mock_constants
import ims.exception.iscsi_exceptions as iscsi_exceptions
from database import Database
from ims.exception.exception import DBException
from ims.interfaces.iscsi import ISCSI


def get_driver_class():
    return Mock


# Do We Need Logging ?
class Mock(ISCSI):
    def __init__(self, fs_config, iscsi_config):
        self.__validate(iscsi_config)
        self.db = Database()

    def __validate(self, iscsi_config):
        try:
            self.db_location = iscsi_config[mock_constants.MOCK_DB_PATH_KEY]
            self.provision_net_ip = iscsi_config[mock_constants.MOCK_IP_KEY]
        except KeyError as e:
            raise iscsi_exceptions.MissingConfigArgumentException(
                e.args[0])

    @property
    def ip(self):
        return self.provision_net_ip

    # Since there is no actual server
    def stop_server(self):
        pass

    def start_server(self):
        pass

    def restart_server(self):
        pass

    def add_target(self, target_name):
        targets = self.list_targets()
        if target_name in targets:
            raise iscsi_exceptions.TargetExistsException()

        try:
            self.db.target.insert(target_name)
        except DBException as e:
            raise iscsi_exceptions.TargetCreationFailedException(str(e))

    def list_targets(self):
        try:
            return self.db.target.fetch_targets()
        except DBException as e:
            raise iscsi_exceptions.ListTargetFailedException(str(e))

    def remove_target(self, target_name):
        targets = self.list_targets()
        if target_name not in targets:
            raise iscsi_exceptions.TargetDoesntExistException()

        try:
            self.db.target.delete_with_name(target_name)
        except DBException as e:
            raise iscsi_exceptions.TargetDeletionFailedException(str(e))
