from abc import ABCMeta

from bmi_exceptions import FileSystemException


# This exception should be raised when Image is not found in file system
class ImageNotFoundException(FileSystemException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name+" Not Found"


# This exception should be raised if some connection issues occured when communicating with file system
class ConnectionException(FileSystemException):
    def __str__(self):
        return "Not Able to Connect to File System"


# this exception should be raised when some operation is called on an image which is busy
class ImageBusyException(FileSystemException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name+" is Busy"


# this exception should be raised when some operation is called on an image that has snapshots
class ImageHasSnapshotException(FileSystemException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name+" has Snapshots"


# this exception should be raised when some operation requires that an image not exist in the filesytem
class ImageExistsException(FileSystemException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name+" Already Exists"


# this exception should be raised when the given image is not opened
class ImageNotOpenedException(FileSystemException):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name+" should be opened before operation"


# this exception should be raised when function that is not supported is called
class FunctionNotSupportedException(FileSystemException):
    def __str__(self):
        return "Function is not Supported"


# this exception should be raised when the arguments are out of range
class ArgumentsOutOfRangeException(FileSystemException):
    def __str__(self):
        return "Arguments are Out of Range"


# this exception should be raised when the config file passed is invalid
class InvalidConfigFileException(FileSystemException):
    def __str__(self):
        return "Invalid Config File"


# this exception should be raised when the config file contains an invalid argument
class IncorrectConfigArgumentException(FileSystemException):
    def __str__(self):
        return "Incorrect Config Argument"


# this exception class is the abstract class for any ceph specific exceptions
class CephFileSystemException(FileSystemException):
    __metaclass__ = ABCMeta
