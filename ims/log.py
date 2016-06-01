import logging
import traceback


def create_logger(name, debug=False, verbose=False):
    logger = logging.getLogger(name)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    formatter = ExceptionFormatter(
        '\n%(levelname)s - %(asctime)s - File "%(pathname)s", line %(lineno)d in %(funcName)s\n%(message)s')
    specfic_file_handler = logging.FileHandler(name + ".log", mode='w')
    all_file_handler = logging.FileHandler("ims.log", mode='a')

    specfic_file_handler.setFormatter(formatter)
    all_file_handler.setFormatter(formatter)

    logger.addHandler(specfic_file_handler)
    logger.addHandler(all_file_handler)

    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


class ExceptionFormatter(logging.Formatter):
    def formatException(self, ei):
        etype, value, tb = ei
        trace = traceback.format_exception(etype,value,tb)
        bases = self.__getbaseclasses(etype.__bases__[0])
        full_class = ".".join(bases) + "."+etype.__name__
        result = "Got "+full_class+" with stacktrace\n"+("".join(trace))
        return result.rstrip('\n')

    def __getbaseclasses(self, c):

        if c.__name__ == "BMIException":
            return []
        else:
            li = self.__getbaseclasses(c.__bases__[0])
            li.append(c.__name__)
            return li
