from exception import ISCSIException


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
