from abc import ABCMeta
from abc import abstractmethod


class ISCSI(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_target(self, target_name):
        '''
        Adding a target for iscsi server
        :return:
        '''
        pass

    @abstractmethod
    def remove_target(self, target_name):
        '''
        Removing a target from iscsi server
        :return:
        '''
        pass

    @abstractmethod
    def list_targets(self):
        '''
        Lists all the targets exposed by iscsi server
        :return:
        '''
        pass

    @abstractmethod
    def start_server(self):
        '''
        Returns the status of iscsi  server
        :return:
        '''
        pass

    @abstractmethod
    def stop_server(self):
        '''
        Stops the iscsi server
        :return:
        '''
        pass

    @abstractmethod
    def restart_server(self):
        '''
        Restart the iscsi server.
        :return:
        '''
        pass

    def persist_targets(self):
        '''
        Restart the iscsi server.
        :return:
        '''
        raise NotImplementedError
