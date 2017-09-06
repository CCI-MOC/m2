from abc import ABCMeta

from ims.exception.exception import FileSystemException


# This exception should be raised when Image is not found in file system
class ImageNotFoundException(FileSystemException):
    @property
    def status_code(self):
        return 404

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + " Not Found"


# This exception should be raised if some connection issues occured when
# communicating with file system
class ConnectionException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Not Able to Connect to File System"


# this exception should be raised when some operation is called on an image
# which is busy
class ImageBusyException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + " is Busy (Could have Clones)"


class SnapshotBusyException(ImageBusyException):
    """
    This exception will be raised if user removes a protected snapshot
    """
    @property
    def status_code(self):
        return ImageBusyException.status_code.fget(self)

    def __init__(self, name):
        ImageBusyException.__init__(self, name)

    def __str__(self):
        return "Snapshot " + self.name + " is protected from removal"


# this exception should be raised when some operation is called on an image
# that has snapshots
class ImageHasSnapshotException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + " has Snapshots"


# this exception should be raised when some operation requires that an image
# not exist in the filesytem
class ImageExistsException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + " Already Exists"


# this exception should be raised when the given image is not opened
class ImageNotOpenedException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + " should be opened before operation"


# this exception should be raised when function that is not supported is called
class FunctionNotSupportedException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Function is not Supported"


# this exception should be raised when the arguments are out of range
class ArgumentsOutOfRangeException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Arguments are Out of Range"


# this exception should be raised when the config file passed is invalid
class InvalidConfigArgumentException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return "Invalid " + self.arg + " argument in config file"


# this exception should be raised when the config file contains an invalid
# argument
class MissingConfigArgumentException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return self.arg + " is incorrect in config file"


class MapFailedException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Map Failed for " + self.name


class UnmapFailedException(FileSystemException):
    @property
    def status_code(self):
        return 500

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Unmap Failed for " + self.name


# this exception class is the abstract class for any ceph specific exceptions
class CephFileSystemException(FileSystemException):
    __metaclass__ = ABCMeta
