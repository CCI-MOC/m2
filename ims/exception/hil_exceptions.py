from ims.exception.exception import HILException


# this exception should be raised when hil reports an authorization failure
class AuthorizationFailedException(HILException):
    @property
    def status_code(self):
        return 403

    def __str__(self):
        return "Authorization Failed"


# this exception should be raised when hil reports an authentication failure
class AuthenticationFailedException(HILException):
    @property
    def status_code(self):
        return 401

    def __str__(self):
        return "Authentication Failed"


# this exception should be raised when some connection issues pop up when
# communicating with hil
class ConnectionException(HILException):
    @property
    def status_code(self):
        return 500

    def __str__(self):
        return "Couldnt connect to HIL"


# this exception is a wrapper for any other hil exception that may pop up
class UnknownException(HILException):
    @property
    def status_code(self):
        return 500

    def __init__(self, status_code, message):
        self.hil_status_code = status_code
        self.message = message

    def __str__(self):
        return "Got status code " + str(
            self.hil_status_code) + " from HIL with message" \
                                    " : " + self.message
