import logging
from config import CONFIG_DICT
from os import stat

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
        _write_audit_log_header()
        _audit.info(message)


def _write_audit_log_header():
    if CONFIG_DICT['LOGGING']:
        if stat(CONFIG_DICT['AUDIT_LOG_FILE']).st_size == 0:
            _formatter2 = logging.Formatter('%(message)s')
            _audit_handler.setFormatter(_formatter2)
            _audit.addHandler(_audit_handler)

            _audit.info(_create_audit_log_header_row())

            _audit_handler.setFormatter(_formatter)
            _audit.addHandler(_audit_handler)


def _create_audit_log_header_row():
    log_entry = []
    log_entry.append('Time')
    log_entry.append('IP address')
    log_entry.append('User type')
    log_entry.append('Title')
    log_entry.append('\'Other\' title')
    log_entry.append('First name(s)')
    log_entry.append('Last name')
    log_entry.append('Username')
    log_entry.append('Date of Birth')
    log_entry.append('Company name')
    log_entry.append('Address line 1')
    log_entry.append('Address line 2')
    log_entry.append('Address line 3')
    log_entry.append('City')
    log_entry.append('Region')
    log_entry.append('Postal code')
    log_entry.append('Country')
    log_entry.append('Detected country')
    log_entry.append('Landline')
    log_entry.append('Mobile')
    log_entry.append('Email')
    log_entry.append('Accepted Ts & Cs')
    log_entry.append('File downloaded')
    return "\"{}\"".format("\",\"".join(log_entry))
