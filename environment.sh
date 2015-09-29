#!/bin/sh
export SETTINGS='dev'
export PYTHONPATH=.
export OVERSEAS_OWNERSHIP_URL='http://localhost:5001'
export SESSION_KEY='my_session_key'
export COUNTRY_LOOKUP_URL='http://www.telize.com/geoip/{}'
export COUNTRY_LOOKUP_FIELD_ID='country'
export COUNTRY_LOOKUP_TIMEOUT_SECONDS='10'
export OVERSEAS_TERMS_FILE='service/static/build/text/ood_terms.txt'
export RECAPTCHA_SITE_KEY=''
export RECAPTCHA_SECRET_KEY=''
