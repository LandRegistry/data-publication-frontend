import os

overseas_ownership_url = os.environ.get('OVERSEAS_OWNERSHIP_URL')
session_key = os.environ.get('SESSION_KEY')
country_lookup_url = os.environ.get('COUNTRY_LOOKUP_URL')
country_lookup_field_id = os.environ.get('COUNTRY_LOOKUP_FIELD_ID')
country_lookup_timeout_seconds = int(os.environ.get('COUNTRY_LOOKUP_TIMEOUT_SECONDS'))
overseas_terms_file = os.environ.get('OVERSEAS_TERMS_FILE')

CONFIG_DICT = {
    'DEBUG': False,
    'LOGGING': True,
    'OVERSEAS_OWNERSHIP_URL': overseas_ownership_url,
    'SESSION_KEY': session_key,
    'WTF_CSRF_SECRET_KEY': session_key,
    'COUNTRY_LOOKUP_URL': country_lookup_url,
    'COUNTRY_LOOKUP_FIELD_ID': country_lookup_field_id,
    'COUNTRY_LOOKUP_TIMEOUT_SECONDS': country_lookup_timeout_seconds,
    'OVERSEAS_TERMS_FILE': overseas_terms_file
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
    CONFIG_DICT['WTF_CSRF_ENABLED'] = False
