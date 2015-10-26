import logging
from os import stat
from functools import wraps

from config import CONFIG_DICT

# create logger
_audit = logging.getLogger('audit_logger')
_audit.setLevel(logging.INFO)
# create handler
_audit_handler = logging.handlers.TimedRotatingFileHandler(CONFIG_DICT['AUDIT_LOG_FILE'],
                                                           when='midnight', utc=True)
_audit_handler.setLevel(logging.INFO)
# create formatter
_formatter = logging.Formatter('\"%(asctime)s\",%(message)s', "%Y-%m-%d %H:%M:%S")
# add formatter
_audit_handler.setFormatter(_formatter)
# add handler to logger
_audit.addHandler(_audit_handler)


def audit(message):
    if CONFIG_DICT['LOGGING']:
        _audit.info(message)


# create logger
_general = logging.getLogger('logger')
_general.setLevel(logging.INFO)
# create handler
_general_handler = logging.handlers.TimedRotatingFileHandler(CONFIG_DICT['GENERAL_LOG_FILE'],
                                                             when='midnight', utc=True)
_general_handler.setLevel(logging.INFO)
# create formatter
_formatter = logging.Formatter(
    '%(asctime)s level=[%(levelname)s] message=[%(message)s] exception=[%(exc_info)s]', "%Y-%m-%d %H:%M:%S")
# add formatter
_general_handler.setFormatter(_formatter)
# add handler to logger
_general.addHandler(_general_handler)


def log(message, level="INFO", exception=None):
    if level.upper() == "CRITICAL":
        msg_level = logging.CRITICAL
    elif level.upper() == "ERROR":
        msg_level = logging.ERROR
    elif level.upper() == "WARNING":
        msg_level = logging.WARNING
    elif level.upper() == "DEBUG":
        msg_level = logging.DEBUG
    else:
        msg_level = logging.INFO

    if CONFIG_DICT['LOGGING']:
        _general.log(level=msg_level, msg=message, exc_info=exception)


def start_stop_logging(original_function):
    @wraps(original_function)
    def wrapped(*args, **kwargs):
        log("{} Start".format(original_function.__name__))
        original = original_function(*args, **kwargs)
        log("{} End".format(original_function.__name__))
        return original
    return wrapped
