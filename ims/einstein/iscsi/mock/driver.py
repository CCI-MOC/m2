from ims.interfaces.iscsi import ISCSI


class Mock(ISCSI):

    def __init__(self, fs_config, iscsi_config):
        # self.db_location = iscsi_config[constants.]
        pass

    def stop_server(self):
        pass

    def start_server(self):
        pass

    def add_target(self, target_name):
        pass

    def restart_server(self):
        pass

    def list_targets(self):
        pass

    def persist_targets(self):
        pass

    def remove_target(self, target_name):
        pass
