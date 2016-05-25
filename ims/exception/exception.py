from abc import ABCMeta


# The base class for all BMI Exceptions
# Made abstract since it is recommended to raise the specific subclass
class BMIException(Exception):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to the file system like ceph
class FileSystemException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to HaaS
class HaaSException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to Database
class DBException(BMIException):
    __metaclass__ = ABCMeta


# The base class for all exceptions related to Shell Script Execution
class ShellScriptException(BMIException):
    __metaclass__ = ABCMeta
