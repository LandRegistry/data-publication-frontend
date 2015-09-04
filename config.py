import os
from typing import Dict, Union

recaptcha_secret_key = os.environ['RECAPTCHA_SECRET_KEY']
recaptcha_site_key = os.environ['RECAPTCHA_SITE_KEY']

CONFIG_DICT = {
    'DEBUG': False,
    'LOGGING': True,
    'RECAPTCHA_SITE_KEY': recaptcha_site_key,
    'RECAPTCHA_SECRET_KEY': recaptcha_secret_key,
} # type: Dict[str, Union[bool, str, int]]

settings = os.environ.get('SETTINGS')

if settings == 'dev':
    CONFIG_DICT['DEBUG'] = True
elif settings == 'test':
    # We do NOT set TESTING to True here as it turns off authentication, and we
    # want to make sure the app behaves the same when running tests locally
    # as it does in production.
    CONFIG_DICT['LOGGING'] = False
    CONFIG_DICT['DEBUG'] = True
