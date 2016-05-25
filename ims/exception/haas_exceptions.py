from exception import HaaSException


# this exception should be raised when haas reports an authorization failure
class AuthorizationFailedException(HaaSException):
    def __str__(self):
        return "Authorization Failed"


# this exception should be raised when haas reports an authentication failure
class AuthenticationFailedException(HaaSException):
    def __str__(self):
        return "Authentication Failed"


# this exception should be raised when some connection issues pop up when communicating with haas
class ConnectionException(HaaSException):
    def __str__(self):
        return "Couldnt connect to HaaS"


# this exception is a wrapper for any other haas exception that may pop up
class UnknownException(HaaSException):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return "Got status code " + str(self.status_code) + " from HaaS with message : " + self.message
