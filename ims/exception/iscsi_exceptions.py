from ims.exception.exception import ISCSIException


class TargetExistsException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Target Already Exists"


class TargetDoesntExistException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Target Doesnt Exist"


class TargetCreationFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Target Creation Failed With Error " + self.error


class TargetDeletionFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Target Deletion Failed With Error " + self.error


class ListTargetFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Listing Targets Failed With Error " + self.error


class StopFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "ISCSI Failed to Stop"


class RestartFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "ISCSI Failed to Restart"


class StartFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "ISCSI Failed to Start"


# this exception should be raised when the config file contains an invalid argument
class MissingConfigArgumentException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return self.arg + " is incorrect in config file"


# this exception should be raised when the config file passed is invalid
class InvalidConfigArgumentException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return "Invalid " + self.arg + " argument in config file"
