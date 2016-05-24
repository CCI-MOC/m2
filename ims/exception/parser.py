import db_exceptions
import file_system_exceptions
import haas_exceptions


# this class parses the given exception and returns the corresponding status code that should be returned to user
class ExceptionParser:
    status_codes = {file_system_exceptions.ImageExistsException: 471,
                    file_system_exceptions.ConnectionException: 472,
                    file_system_exceptions.ImageBusyException: 473,
                    file_system_exceptions.ImageHasSnapshotException: 474,
                    file_system_exceptions.ImageNotFoundException: 404,
                    file_system_exceptions.FunctionNotSupportedException: 476,
                    file_system_exceptions.ArgumentsOutOfRangeException: 477,
                    db_exceptions.ImageNotFoundException: 404,
                    db_exceptions.ProjectNotFoundException: 404,
                    haas_exceptions.AuthenticationFailedException: 401,
                    haas_exceptions.AuthorizationFailedException: 403}

    # returns the status code as per the class of the exception
    # default status code is 500
    def parse(self, ex):
        return ExceptionParser.status_codes.get(type(ex), 500)
