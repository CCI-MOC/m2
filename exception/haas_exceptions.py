from bmi_exceptions import HaaSException


class AuthorizationFailedException(HaaSException):
    def __str__(self):
        return "Authorization Failed"


class AuthenticationFailedException(HaaSException):
    def __str__(self):
        return "Authentication Failed"


class ConnectionException(HaaSException):
    def __str__(self):
        return "Couldnt connect to HaaS"


class UnknownException(HaaSException):
    def __init__(self, status_code,message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return "Got status code " + str(self.status_code) + " from HaaS with message : " + self.message
