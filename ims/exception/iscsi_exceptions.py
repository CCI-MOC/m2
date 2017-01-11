from ims.exception.exception import ISCSIException


# this exception should be raised when the shell script is called on a node that is already in use
class NodeAlreadyInUseException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Node Already in Use"


# this exception should be raised when the shell script is called on a node that is already unmapped
class NodeAlreadyUnmappedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Node Already Unmapped"


class InvalidConfigException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Invalid ietd.conf"


class DuplicatesException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, names):
        self.names = names

    def __str__(self):
        return "Found Duplicates for " + ",".join(self.names)


class MountException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, names):
        self.names = names

    def __str__(self):
        return "Failed to mount " + ",".join(self.names)


class UpdateConfigFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Failed to update config with error " + self.error


class ReadConfigFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Failed to update config with error " + self.error


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
