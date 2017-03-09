from ims.exception.exception import ShellException


class CommandFailedException(ShellException):
    """ Should be raised when executing a command fails """

    @property
    def status_code(self):
        return 500

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Shell command failed with error {0}".format(self.error)


class ServiceCommandFailedException(ShellException):
    """ Should be raised when one of the service command fails """

    @property
    def status_code(self):
        return 500

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "Service command failed with status {0}".format(self.status)
