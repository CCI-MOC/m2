from file_system_exceptions import *


# this class parses the given exception and returns the corresponding status code that should be returned to user
class ExceptionParser:
    status_codes = {ImageExistsException: 471,
                    ConnectionException: 472,
                    ImageBusyException: 473,
                    ImageHasSnapshotException: 474,
                    ImageNotFoundException: 475,
                    FunctionNotSupportedException: 476,
                    ArgumentsOutOfRangeException: 477}

    # returns the status code as per the class of the exception
    # default status code is 500
    def parse(self, ex):
        return ExceptionParser.status_codes.get(type(ex), 500)
