"""This module provides the ipxe driver interfaces"""

from abc import ABCMeta, abstractmethod


class ipxe:
    """description for ipxe"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def ipxe(self, conf_file):
        """Set up ipxe"""
        pass

    @abstractmethod
    def generate_ipxe_file(self, node_name, target_name):
        """Generate ipxe file"""
        pass
