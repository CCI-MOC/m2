from ims.exception.exception import HaaSException


# this exception should be raised when haas reports an authorization failure
class AuthorizationFailedException(HaaSException):
    @property
    def status_code(self):
        return 403

    def __str__(self):
        return "Authorization Failed"


# this exception should be raised when haas reports an authentication failure
class AuthenticationFailedException(HaaSException):
    @property
    def status_code(self):
        return 401

    def __str__(self):
        return "Authentication Failed"


# this exception should be raised when some connection issues pop up when
# communicating with haas
class ConnectionException(HaaSException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Couldnt connect to HaaS"


class NotAttachedException(HaaSException):
    @property
    def status_code(self):
        return 400

    def __str__(self):
        return "Node Not Attached to Nic"


class AttachedException(HaaSException):
    @property
    def status_code(self):
        return 409

    def __str__(self):
        return "Node Already Attached to Nic"


# this exception is a wrapper for any other haas exception that may pop up
class UnknownException(HaaSException):
    @property
    def status_code(self):
        return 500

    def __init__(self, status_code, message):
        self.haas_status_code = status_code
        self.message = message

    def __str__(self):
        return "Got status code " + str(
            self.haas_status_code) + " from HaaS with message" \
                                     " : " + self.message
