from ims.exception.exception import ISCSIException


# this exception should be raised when the target already exists
class TargetExistsException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Node Already in Use"


# this exception should be raised when the target doesnt exist
class TargetDoesntExistException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Node Already Unmapped"


class TargetCreationFailed(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Target Creation Failed with error {0}".format(self.error)


class TargetDeletionFailed(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Target Deletion Failed with error {0}".format(self.error)


class ListTargetFailedException(ISCSIException):
    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "List Target Failed with error {0}".format(self.error)


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
