import inspect
import logging
import logging.handlers
import traceback

import ims.common.config as config

loggers = {}


def log(func):
    def func_wrapper(*args, **kwargs):
        name = inspect.getmodule(func).__name__
        cfg = config.get()
        logger = create_logger(cfg.logs_url, name, cfg.logs_debug,
                               cfg.logs_verbose)
        rec = inspect.stack()[1]
        file = rec[1]
        line = rec[2]
        func_name = rec[3]
        base_msg = str.format("File '{0}', line {1} in {2}\n", file, line,
                              func_name)
        logger.debug(base_msg + "Entering %s with Parameters\n%s",
                     func.__name__, format_args(*args, **kwargs),
                     extra={'special': True})
        ret = func(*args, **kwargs)
        if func.__name__ == "__init__":
            logger.info(base_msg + "Successfully Initialised %s instance",
                        type(list(args)[0]).__name__, extra={'special': True})
        else:
            logger.info(base_msg + "Successfully Executed %s",
                        func.__name__, extra={'special': True})
        logger.debug(base_msg + "Exiting %s with return value = %s",
                     func.__name__, ret, extra={'special': True})

    return func_wrapper


def format_args(*args, **kwargs):
    string = ""
    l = list(args)
    for arg in l:
        string += str(arg) + "\n"

    for k, v in kwargs.iteritems():
        string += str(k) + " = " + str(v) + "\n"

    if string == "":
        return "No Parameters"
    return string.rstrip('\n')


def create_logger(base_url, name, debug=False, verbose=False):
    if name in loggers:
        return loggers[name]

    logger = logging.getLogger(name)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    formatter = BMIFormatter()
    specific_file_handler = logging.FileHandler(base_url + name + ".log",
                                                mode='a')
    all_file_handler = logging.handlers.RotatingFileHandler(
        base_url + "ims.log", mode='a', maxBytes=10000000, backupCount=10)

    specific_file_handler.setFormatter(formatter)
    all_file_handler.setFormatter(formatter)

    logger.addHandler(specific_file_handler)
    logger.addHandler(all_file_handler)

    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    loggers[name] = logger
    return logger


class BMIFormatter(logging.Formatter):
    def formatException(self, ei):
        etype, value, tb = ei
        trace = traceback.format_exception(etype, value, tb)
        bases = self.__getbaseclasses(etype.__bases__[0])
        full_class = ".".join(bases) + "." + etype.__name__
        result = "Got " + full_class + " with stacktrace\n" + ("".join(trace))
        return result.rstrip('\n')

    def format(self, record):
        normal_formatter = logging.Formatter(
            '\n%(levelname)s - %(asctime)s - File "%(pathname)s", line %(lineno)d in %(funcName)s\n%(message)s')
        decorator_formatter = logging.Formatter(
            '\n%(levelname)s - %(asctime)s - %(message)s')
        extra = record.__dict__
        try:
            if extra['special']:
                return decorator_formatter.format(record)
        except KeyError:
            return normal_formatter.format(record)

    def __getbaseclasses(self, c):

        if c.__name__ == "BMIException":
            return []
        else:
            li = self.__getbaseclasses(c.__bases__[0])
            li.append(c.__name__)
            return li
