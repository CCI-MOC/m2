from abc import ABCMeta
from abc import abstractproperty


# The base class for all BMI Exceptions
# Made abstract since it is recommended to raise the specific subclass
class BMIException(Exception):
    __metaclass__ = ABCMeta

    @abstractproperty
    def status_code(self):
        pass


# The base class for all exceptions related to the file system like ceph
class FileSystemException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to HIL
class HILException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to Database
class DBException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to ISCSI
class ISCSIException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to the BMI Config Parser
class ConfigException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to DHCP
class DHCPException(BMIException):
    __metaclass__ = ABCMeta


class ShellException(BMIException):
    """ The Base Class for all exceptions related to Shell """
    __metaclass__ = ABCMeta


# this exception should be raised when a user who is not a bmi admin tries
# admin level functions
class AuthorizationFailedException(BMIException):
    @property
    def status_code(self):
        return 403

    def __str__(self):
        return "User Does Not Have Admin Role"


class RegistrationFailedException(BMIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, node, error):
        self.node = node
        self.error = error

    def __str__(self):
        return "Failed to register " + self.node + " due to " + self.error
