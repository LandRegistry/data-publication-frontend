#!/bin/sh
export SETTINGS='dev'
export PYTHONPATH=.
export OVERSEAS_OWNERSHIP_URL='http://localhost:5001'
export SESSION_KEY='my_session_key'
export OVERSEAS_TERMS_FILE='service/static/build/text/ood_terms.txt'
export RECAPTCHA_PUBLIC_KEY='6Lfuew0TAAAAAL-MOavC2hVNtnwAXipG3B6Glvay'
export RECAPTCHA_PRIVATE_KEY='6Lfuew0TAAAAAH1HRBzy-1tteGz0dM38GiZtO_rL'
export DO_RECAPTCHA='True'
export LOGGING_LEVEL='INFO' # From DEBUG, INFO, WARNING, ERROR and CRITICAL
export GENERAL_LOG_FILE='logs/data-publication-frontend.log'
export AUDIT_LOG_FILE='logs/data-publication-frontend-audit.csv'
export GOOGLE_ANALYTICS_PROPERTY_ID=''
export URL_PREFIX=''
export AWS_BASE_URL=''
