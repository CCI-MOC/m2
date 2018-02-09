"""This module provides interfaces for Auth"""

from abc import ABCMeta, abstractmethod


class AuthServer:
    """Desecription for Authserver"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_auth_backend(self):
        """Return the autherization"""
        pass

    @abstractmethod
    def require_admin(self):
        """Assure that admin authority is required"""
        pass

    @abstractmethod
    def require_access(self, entityId):
        """Assure entity's authority to take specific action"""
        pass
