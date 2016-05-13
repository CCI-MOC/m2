from bmi_exceptions import *
from file_system_exceptions import *


class ExceptionParser:
    status_codes = {ImageExistsException: 471,
                    ConnectionException: 472,
                    ImageBusyException: 473,
                    ImageHasSnapshotException: 474,
                    ImageNotFoundException: 475,
                    FunctionNotSupportedException: 476,
                    ArgumentsOutOfRangeException: 477}

    def parse(self, ex):
        return ExceptionParser.status_codes.get(type(ex),500)
