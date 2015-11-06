#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, session, request, abort, Response
from service import app, logger_config
#import service.logger_config
from service.my_forms import (UserTypeForm, PersonalForm, CompanyForm, AddressForm, TelForm,
                              CompanyTelForm, TermsForm, ReCaptchaForm)
import requests
import json
from hurry.filesize import size, alternative
import datetime
import uuid
import re
from werkzeug.contrib.fixers import ProxyFix

# Apply fix for obtaining IP address from behind a proxy.
app.wsgi_app = ProxyFix(app.wsgi_app)

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

BREADCRUMBS = [
    {"text": "Dataset details", "url": app.config['START_PAGE']},
    {"text": "User type", "url": "/usertype"},
    {"text": "Personal details", "url": "/personal"},
    {"text": "Address details", "url": "/address"},
    {"text": "Contact details", "url": "/tel"},
    {"text": "Human validation check", "url": "/recaptcha"},
    {"text": "Terms and conditions", "url": "/terms"},
    {"text": "Data download", "url": "/dataset"},
    {"text": "Expired link", "url": ""}
]

URL_PREFIX = app.config['URL_PREFIX']

RECAPTCHA_PRIVATE_KEY = app.config['RECAPTCHA_PRIVATE_KEY']

logger = logger_config.LoggerConfig(app)
logger.setup_logger(__name__)
logger.setup_audit_logger()


@app.route(URL_PREFIX + '/cookies/')
@logger.start_stop_logging
def cookies():
    breadcrumbs = [{"text": "Dataset details", "url": app.config['START_PAGE']},
                   {"text": "Cookies", "url": "/cookies"}]
    return render_template('cookies.html', breadcrumbs=breadcrumbs)


@app.route(URL_PREFIX + '/')
@app.route(URL_PREFIX + '/usertype/')
@logger.start_stop_logging
def user_type(usertype_form=None):
    if usertype_form is None:
        usertype_form = UserTypeForm()
        populate_form(usertype_form)

        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        session['ip_address'] = ip_address
    return render_template('usertype.html', form=usertype_form, breadcrumbs=BREADCRUMBS[:2])


@app.route(URL_PREFIX + '/usertype/validation', methods=['POST'])
@logger.start_stop_logging
def validate_usertype_details():
    usertype_form = UserTypeForm()
    populate_session(usertype_form)
    if 'session_id' not in session or session['session_id'] is not '':
        session['session_id'] = uuid.uuid4()
    if usertype_form.validate_on_submit():
        return redirect(url_for("personal"))
    return user_type(usertype_form)

@app.route(URL_PREFIX + '/personal/')
@logger.start_stop_logging
def personal(personal_form=None):
    if personal_form is None:
        if 'user_type' not in session:
            return redirect(url_for('user_type'))
        elif session['user_type'] == 'Company':
            personal_form = CompanyForm()
        else:
            personal_form = PersonalForm()
        populate_form(personal_form)
    return render_template("personal.html", form=personal_form, breadcrumbs=BREADCRUMBS[:3])


@app.route(URL_PREFIX + '/personal/validation', methods=['POST'])
@logger.start_stop_logging
def validate_personal_details():
    if 'user_type' not in session:
        return redirect(url_for('user_type'))
    elif session['user_type'] == 'Company':
        personal_form = CompanyForm()
    else:
        personal_form = PersonalForm()
    populate_session(personal_form)
    if personal_form.validate_on_submit():
        session['personal_screen'] = 'Complete'
        return redirect(url_for("address"))
    return personal(personal_form)

@app.route(URL_PREFIX + '/address/')
@logger.start_stop_logging
def address(address_form=None):
    if address_form is None:
        if 'personal_screen' not in session:
            return redirect(url_for("personal"))
        address_form = AddressForm()
        populate_form(address_form)
    return render_template("address.html", form=address_form, breadcrumbs=BREADCRUMBS[:4])


@app.route(URL_PREFIX + '/address/validation', methods=['POST'])
@logger.start_stop_logging
def validate_address_details():
    address_form = AddressForm()
    populate_session(address_form)
    if address_form.validate_on_submit():
        session['address_screen'] = 'Complete'
        return redirect(url_for("tel"))
    return address(address_form)

@app.route(URL_PREFIX + '/tel/')
@logger.start_stop_logging
def tel(tel_form=None):
    if tel_form is None:
        if 'address_screen' not in session:
            return redirect(url_for('address'))
        elif session['user_type'] == 'Company':
            tel_form = CompanyTelForm()
        else:
            tel_form = TelForm()
        populate_form(tel_form)
    return render_template('tel.html', form=tel_form, breadcrumbs=BREADCRUMBS[:5])


@app.route(URL_PREFIX + '/tel/validation', methods=['POST'])
@logger.start_stop_logging
def validate_telephone_details():
    if 'user_type' not in session:
        return redirect(url_for('user_type'))
    elif session['user_type'] == 'Company':
        tel_form = CompanyTelForm()
    else:
        tel_form = TelForm()
    populate_session(tel_form)
    if tel_form.validate_on_submit():
        session['tel_screen'] = 'Complete'
        return redirect(url_for('recaptcha'))
    return tel(tel_form)

@app.route(URL_PREFIX + '/recaptcha/')
@logger.start_stop_logging
def recaptcha(recaptcha_form=None):
    if recaptcha_form is None:
        if 'tel_screen' not in session:
            return redirect(url_for('tel'))
        recaptcha_form = ReCaptchaForm()
        populate_form(recaptcha_form)
    return render_template('recaptcha.html', form=recaptcha_form,
                           recaptcha_public_key=app.config['RECAPTCHA_PUBLIC_KEY'], breadcrumbs=BREADCRUMBS[:6])


@app.route(URL_PREFIX + '/recaptcha/validation', methods=['POST'])
@logger.start_stop_logging
def validate_recaptcha():
    if app.config['DO_RECAPTCHA'] == 'False':
        session['recaptcha_result'] = 'pass'
        return redirect(url_for('terms'))
    recaptcha_form = ReCaptchaForm()
    populate_session(recaptcha_form)
    if recaptcha_form.validate_on_submit():
        session['recaptcha_result'] = 'pass'
        return redirect(url_for('terms'))
    session['recaptcha_result'] = 'fail'
    return recaptcha(recaptcha_form)

@app.route(URL_PREFIX + '/terms/')
@logger.start_stop_logging
def terms(terms_form=None):
    if terms_form is None:
        if 'recaptcha_result' not in session or session['recaptcha_result'] == 'fail':
            return redirect(url_for('recaptcha'))
        terms_form = TermsForm()
        populate_form(terms_form)
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms.html', form=terms_form, text=data, breadcrumbs=BREADCRUMBS[:7])

@app.route(URL_PREFIX + '/printable_terms/')
@logger.start_stop_logging
def printable_terms():
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms_printer_friendly.html', text=data)


@app.route(URL_PREFIX + '/decline_terms/')
@logger.start_stop_logging
def decline_terms():
    session['terms'] = 'declined'
    logger.audit(format_session_info_for_audit())
    return render_template('decline_terms.html', govuk_page=app.config['START_PAGE'])

@app.route(URL_PREFIX + '/dataset/', methods=['GET'])
@app.route(URL_PREFIX + '/dataset', methods=['POST'])
@logger.start_stop_logging
def get_data():
    if request.method == 'POST' or ('terms' in session
                                    and session['terms'] == 'accepted'):
        session['terms'] = 'accepted'

        logger.audit(format_session_info_for_audit())

        response = requests.get(app.config['OVERSEAS_OWNERSHIP_URL'] +
                                "/list-files/overseas")
        response_json = response.json()

        # Get the link
        files = response_json['File_List']

        datasets = []

        for link in files:

            # Check link is in valid format
            pattern = re.compile(r'OV+_[A-Za-z]+_20\d{2}_\d{2}.[A-Za-z]{3}')
            if pattern.match(link["Name"]):

                # Split into a list of words and reorder the month and year
                words = link["Name"].split("_")
                # Display the month in name format
                words[3] = MONTHS[int(words[3][:2]) - 1]
                amazon_attributes = extract_url_variables(link['URL'])
                generated_url = url_for('hide_url', filename=link['Name'],
                                        amazon_date=amazon_attributes['X-Amz-Date'],
                                        link_duration=response_json['Link_Duration'],
                                        credentials=amazon_attributes['X-Amz-Credential'],
                                        signature=amazon_attributes['X-Amz-Signature'])
                if words[1].upper() == "FULL":
                    new_link = "Overseas Dataset (" + words[3] + " " + words[2] + ")"
                    datasets.append({"filename": new_link, "url": generated_url,
                                          "size": size(link["Size"], system=alternative)})
                else:
                    continue

        duration = response_json['Link_Duration'] - 1
        minutes, seconds = divmod(duration, 60)
        duration = "{} minute(s) {} second(s)".format(minutes, seconds)

        return render_template('data.html', datasets=datasets, duration=duration, breadcrumbs=BREADCRUMBS[:8])
    else:
        return redirect(url_for('terms'))


@app.route(URL_PREFIX + '/dataset/download/<filename>/<amazon_date>/<link_duration>/<credentials>/<signature>/')
@logger.start_stop_logging
def hide_url(filename, amazon_date, link_duration, credentials, signature):
    if ('user_type' not in session
            or 'personal_screen' not in session
            or 'address_screen' not in session
            or 'tel_screen' not in session
            or 'recaptcha_result' not in session or session['recaptcha_result'] == 'fail'
            or 'terms' not in session or session['terms'] != 'accepted'):
        return redirect(url_for('terms'))

    expiry_date = (datetime.datetime.strptime(amazon_date, "%Y%m%dT%H%M%SZ")
                   + datetime.timedelta(seconds=int(link_duration)))

    if datetime.datetime.utcnow() >= expiry_date:
        return render_template('download_expired.html', url_prefix=URL_PREFIX)

    logger.audit(format_session_info_for_audit(download_filename=filename))
    base_url = (
        "{}overseas/{}?X-Amz-SignedHeaders=host&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date={}"
        "&X-Amz-Expires={}&X-Amz-Credential={}&X-Amz-Signature={}")

    return redirect(
        base_url.format(app.config['AWS_BASE_URL'], filename, amazon_date, int(link_duration),
                        credentials, signature))


def extract_url_variables(url):
    parts = url.split('?')
    pairs = parts[1].split('&')
    attributes = dict(entry.split('=') for entry in pairs)
    return attributes


def populate_form(form):
    excluded_fields = ['csrf_token']
    for field in form:
        if field.name not in excluded_fields and field.name in session and session[
                field.name] is not None:
            field.data = session[field.name].strip() if isinstance(session[field.name], str) else \
                session[field.name]


def populate_session(form):
    excluded_fields = ['csrf_token']
    for field in form:
        if field.name not in excluded_fields and field.data != 'None' and field.data is not None:
            session[field.name] = field.data.strip() if isinstance(field.data, str) else field.data


def format_session_info_for_audit(download_filename=None):
    log_entry = []
    log_entry.append(session['ip_address'])
    log_entry.append(str(session['session_id']))
    log_entry.append(session['user_type'])
    log_entry.append(session['title'])
    log_entry.append(session['other_title'] if 'other_title' in session
                                               and session['title'] == 'Other' else '')
    log_entry.append(session['first_name'])
    log_entry.append(session['last_name'])
    log_entry.append("{}/{}/{}".format(session['day'], session['month'], session['year']))
    log_entry.append(session['company_name'] if 'company_name' in session
                                                and session['user_type'] == 'Company' else '')
    log_entry.append(session['address_line_1'])
    log_entry.append(session['address_line_2'] if 'address_line_2' in session else '')
    log_entry.append(session['address_line_3'] if 'address_line_3' in session else '')
    log_entry.append(session['city'] if 'city' in session else '')
    log_entry.append(session['region'] if 'region' in session else '')
    log_entry.append(session['postal_code'] if 'postal_code' in session else '')
    log_entry.append(session['country'])
    log_entry.append(session['landline'] if 'landline' in session else '')
    log_entry.append(session['mobile'] if 'mobile' in session else '')
    log_entry.append(session['email'])
    log_entry.append(session['terms'])
    log_entry.append(download_filename if download_filename else '')
    return "\"{}\"".format("\",\"".join(log_entry))


@app.route('/health', methods=['GET'])
def health_check():
    try:
        response = requests.get(app.config['OVERSEAS_OWNERSHIP_URL'] + "/health")
        status_code = response.status_code
        if status_code != 200:
            error = response.json()['error']
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError):
        status_code = 500
        error = 'Cannot connect to backend service'

    status = "OK" if status_code == 200 else "Error"
    response_body = {'status': status}

    if status_code != 200:
        response_body['error'] = error

    return Response(
        json.dumps(response_body),
        status=status_code,
        mimetype='application/json',
    )
