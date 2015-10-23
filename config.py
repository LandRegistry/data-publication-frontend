import os

overseas_ownership_url = os.environ.get('OVERSEAS_OWNERSHIP_URL')
session_key = os.environ.get('SESSION_KEY')
overseas_terms_file = os.environ.get('OVERSEAS_TERMS_FILE')
recaptcha_private_key = os.environ.get('RECAPTCHA_PRIVATE_KEY')
recaptcha_public_key = os.environ.get('RECAPTCHA_PUBLIC_KEY')
do_recaptcha = os.environ.get('DO_RECAPTCHA')
audit_log_file = os.environ.get('AUDIT_LOG_FILE')
ga_property_id = os.environ.get('GOOGLE_ANALYTICS_PROPERTY_ID')
url_prefix = os.environ.get('URL_PREFIX')
aws_base_url = os.environ.get('AWS_BASE_URL')

CONFIG_DICT = {
    'DEBUG': False,
    'LOGGING': True,
    'OVERSEAS_OWNERSHIP_URL': overseas_ownership_url,
    'SESSION_KEY': session_key,
    'WTF_CSRF_SECRET_KEY': session_key,
    'OVERSEAS_TERMS_FILE': overseas_terms_file,
    'RECAPTCHA_PUBLIC_KEY': recaptcha_public_key,
    'RECAPTCHA_PRIVATE_KEY': recaptcha_private_key,
    'DO_RECAPTCHA': do_recaptcha,
    'AUDIT_LOG_FILE': audit_log_file,
    'GOOGLE_ANALYTICS_PROPERTY_ID': ga_property_id,
    'URL_PREFIX': url_prefix,
    'AWS_BASE_URL': aws_base_url
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
