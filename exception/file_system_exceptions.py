from abc import ABCMeta

from bmi_exceptions import FileSystemException


class ImageNotFoundException(FileSystemException):
    def __str__(self):
        return "Image Not Found"


class ConnectionException(FileSystemException):
    def __str__(self):
        return "Not Able to Connect to File System"


class ImageBusyException(FileSystemException):
    def __str__(self):
        return "Image is Busy"


class ImageHasSnapshotException(FileSystemException):
    def __str__(self):
        return "Image has Snapshots"


class ImageExistsException(FileSystemException):
    def __str__(self):
        return "Image Already Exists"

class ImageNotOpenedException(FileSystemException):
    def __str__(self):
        return "Image should be opened before operation"


class FunctionNotSupportedException(FileSystemException):
    def __str__(self):
        return "Function is not Supported"


class ArgumentsOutOfRangeException(FileSystemException):
    def __str__(self):
        return "Arguments are Out of Range"

class InvalidConfigFileException(FileSystemException):
    def __str__(self):
        return "Invalid Config File"

class IncorrectConfigArgumentException(FileSystemException):
    def __str__(self):
        return "Incorrect Config Argument"


class CephFileSystemException(FileSystemException):
    __metaclass__ = ABCMeta
