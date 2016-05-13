from abc import ABCMeta
from exception import BMIException


class FileSystemException(BMIException):
    __metaclass__ = ABCMeta


class HaaSException(BMIException):
    __metaclass__ = ABCMeta


class DBException(BMIException):
    __metaclass__ = ABCMeta

class ShellScriptException(BMIException):
    __metaclass__ = ABCMeta