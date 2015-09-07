import os

CONFIG_DICT = {
    'DEBUG': False,
    'LOGGING': True
}

settings = os.environ.get('SETTINGS')
overseas_ownership_url = os.environ.get('OVERSEAS_OWNERSHIP_URL')

if settings == 'dev':
    CONFIG_DICT['DEBUG'] = True
elif settings == 'test':
    # We do NOT set TESTING to True here as it turns off authentication, and we
    # want to make sure the app behaves the same when running tests locally
    # as it does in production.
    CONFIG_DICT['LOGGING'] = False
    CONFIG_DICT['DEBUG'] = True
