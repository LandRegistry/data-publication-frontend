#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, session, request
from service import app
import service.logger_config as logger
from service.my_forms import (UserTypeForm, PersonalForm, CompanyForm, AddressForm, TelForm,
                              CompanyTelForm, TermsForm, ReCaptchaForm)
import requests
import json
from hurry.filesize import size, alternative
import datetime
import uuid

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

RECAPTCHA_PRIVATE_KEY = app.config['RECAPTCHA_PRIVATE_KEY']

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('ood.html')


@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

@app.route('/usertype/')
@app.route('/usertype')
def user_type(usertype_form=None):
    if usertype_form is None:
        usertype_form = UserTypeForm()
        populate_form(usertype_form)
    return render_template('usertype.html', form=usertype_form)


@app.route('/usertype/validation', methods=['POST'])
def validate_usertype_details():
    usertype_form = UserTypeForm()
    populate_session(usertype_form)
    if 'session_id' not in session or session['session_id'] is not '':
        session['session_id'] = uuid.uuid4()
    if usertype_form.validate_on_submit():
        return redirect(url_for("personal"))
    return user_type(usertype_form)

@app.route('/personal/')
@app.route('/personal')
def personal(personal_form=None):
    if personal_form is None:
        if 'user_type' not in session:
            return redirect(url_for('user_type'))
        elif session['user_type'] == 'Company':
            personal_form = CompanyForm()
        else:
            personal_form = PersonalForm()
        populate_form(personal_form)
    return render_template("personal.html", form=personal_form)


@app.route('/personal/validation', methods=['POST'])
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

@app.route('/address/')
@app.route('/address')
def address(address_form=None):
    if address_form is None:
        if 'personal_screen' not in session :
            return redirect(url_for("personal"))
        address_form = AddressForm()
        if 'country' not in session or session['country'] is '':
            ip_address = request.remote_addr

            # Use this code when running locally to get IP address
#             my_ip_address = requests.get('http://www.telize.com/jsonip',
#                                          timeout=app.config['COUNTRY_LOOKUP_TIMEOUT_SECONDS'])
#             if my_ip_address.status_code == 200:
#                 ip_address = my_ip_address.json()['ip']
#             else:
#                 ip_address = "81.128.179.58"

            session['ip_address'] = ip_address

            try:
                geo = requests.get(app.config['COUNTRY_LOOKUP_URL'].format(ip_address),
                                   timeout=app.config['COUNTRY_LOOKUP_TIMEOUT_SECONDS'])
                if geo.status_code == 200 and app.config['COUNTRY_LOOKUP_FIELD_ID'] in geo.json():
                    address_form.country.data = geo.json()[app.config['COUNTRY_LOOKUP_FIELD_ID']]
                    session['detected_country'] = geo.json()[app.config['COUNTRY_LOOKUP_FIELD_ID']]
                else:
                    session['detected_country'] = '(Could not detect)'
            except requests.exceptions.Timeout:
                session['detected_country'] = '(Could not detect)'
            except requests.exceptions.ConnectionError:
                session['detected_country'] = '(Could not detect)'
        populate_form(address_form)
    return render_template("address.html", form=address_form)


@app.route('/address/validation', methods=['POST'])
def validate_address_details():
    address_form = AddressForm()
    populate_session(address_form)
    if address_form.validate_on_submit():
        session['address_screen'] = 'Complete'
        return redirect(url_for("tel"))
    return address(address_form)

@app.route('/tel/')
@app.route('/tel')
def tel(tel_form=None):
    if tel_form is None:
        if 'address_screen' not in session:
            return redirect(url_for('address'))
        elif session['user_type'] == 'Company':
            tel_form = CompanyTelForm()
        else:
            tel_form = TelForm()
        populate_form(tel_form)
    return render_template('tel.html', form=tel_form)


@app.route('/tel/validation', methods=['POST'])
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

@app.route('/recaptcha/')
@app.route('/recaptcha')
def recaptcha(recaptcha_form=None):
    if recaptcha_form is None:
        if 'tel_screen' not in session:
            return redirect(url_for('tel'))
        recaptcha_form = ReCaptchaForm()
        populate_form(recaptcha_form)
    return render_template('recaptcha.html', form=recaptcha_form)


@app.route('/recaptcha/validation', methods=['POST'])
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

@app.route('/terms/')
@app.route('/terms')
def terms(terms_form=None):
    if terms_form is None:
        if 'recaptcha_result' not in session or session['recaptcha_result'] == 'fail':
            return redirect(url_for('recaptcha'))
        terms_form = TermsForm()
        populate_form(terms_form)
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms.html', form=terms_form, text=data)

@app.route('/printable_terms/')
@app.route('/printable_terms')
def printable_terms():
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms_printer_friendly.html', text=data)


@app.route('/decline_terms')
def decline_terms():
    session['terms_accepted'] = False
    logger.audit(format_session_info_for_audit())
    return redirect(url_for('index'))

@app.route('/data/', methods=['GET', 'POST'])
@app.route('/data', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        session['terms_accepted'] = True

        logger.audit(format_session_info_for_audit())

        response = requests.get(app.config['OVERSEAS_OWNERSHIP_URL'] +
                                "/list-files/overseas-ownership")
        response_json = response.json()

        # Get the link
        files = response_json['File_List']

        full_datasets = []
        updated_datasets = []

        for link in files:
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

            if words[1] == "FULL":
                new_link = "Overseas Dataset (" + words[3] + " " + words[2] + ")"
                full_datasets.append({"filename": new_link, "url": generated_url,
                                      "size": size(link["Size"], system=alternative)})
            else:
                update_link = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
                updated_datasets.append({"filename": update_link, "url": generated_url,
                                         "size": size(link["Size"], system=alternative)})

        duration = response_json['Link_Duration']
        minutes, seconds = divmod(duration, 60)
        duration = "{} minute(s) {} second(s)".format(minutes, seconds)

        return render_template('data.html', fullDatasets=full_datasets,
                               updatedDatasets=updated_datasets, duration=duration)
    else:
        return redirect(url_for('terms'))

@app.route('/data/download/<filename>/<amazon_date>/<link_duration>/<credentials>/<signature>/')
@app.route('/data/download/<filename>/<amazon_date>/<link_duration>/<credentials>/<signature>')
def hide_url(filename, amazon_date, link_duration, credentials, signature):
    logger.audit(format_session_info_for_audit(download_filename=filename))
    base_url = \
        "https://s3.eu-central-1.amazonaws.com/data.landregistry.gov.uk/overseas-ownership/{}" \
        "?X-Amz-SignedHeaders=host&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date={}" \
        "&X-Amz-Expires={}&X-Amz-Credential={}&X-Amz-Signature={}"
    return redirect(
        base_url.format(filename, amazon_date, int(link_duration), credentials, signature))


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
    log_entry.append(session['username'])
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
    log_entry.append(session['detected_country'] if 'detected_country' in session else '')
    log_entry.append(session['landline'] if 'landline' in session else '')
    log_entry.append(session['mobile'] if 'mobile' in session else '')
    log_entry.append(session['email'])
    log_entry.append(str(session['terms_accepted']))
    log_entry.append(download_filename if download_filename else '')
    return "\"{}\"".format("\",\"".join(log_entry))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
