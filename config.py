import os

overseas_ownership_url = os.environ.get('OVERSEAS_OWNERSHIP_URL')

CONFIG_DICT = {
    'DEBUG': False,
    'LOGGING': True,
    'OVERSEAS_OWNERSHIP_URL': overseas_ownership_url
}

settings = os.environ.get('SETTINGS')

if settings == 'dev':
    CONFIG_DICT['DEBUG'] = True
elif settings == 'test':
    # We do NOT set TESTING to True here as it turns off authentication, and we
    # want to make sure the app behaves the same when running tests locally
    # as it does in production.
    CONFIG_DICT['LOGGING'] = False
    CONFIG_DICT['DEBUG'] = True
