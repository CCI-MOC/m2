"""This module provides interfaces for Target"""
from abc import ABCMeta, abstractmethod


class Target:
    """Description for this class"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def target(self, conf_file):
        """Creates a target"""
        pass

    @abstractmethod
    def add_target(self, clone_ceph_name):
        """Add a new target with given image"""
        pass

    @abstractmethod
    def remove_target(self, clone_ceph_name):
        """Remove a target"""
        pass

    @abstractmethod
    def delete_target(self, clone_ceph_name):
        """delete a target"""
        pass

    @abstractmethod
    def list_targets(self):
        """Show list of targets"""
        pass
