import logging
from service.server import app
from os import stat

# create logger
_audit = logging.getLogger('audit_logger')
_audit.setLevel(logging.INFO)
# create handler
_audit_handler = logging.handlers.TimedRotatingFileHandler(app.config['AUDIT_LOG_FILE'],
                                                           when='midnight', utc=True)
_audit_handler.setLevel(logging.INFO)
# create formatter
_formatter = logging.Formatter('\"%(asctime)s\",%(message)s', "%Y-%m-%d %H:%M:%S")
# add formatter
_audit_handler.setFormatter(_formatter)
# add handler to logger
_audit.addHandler(_audit_handler)


def audit(message):
    if app.config['LOGGING']:
        _audit.info(message)
