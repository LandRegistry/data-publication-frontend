#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, session, request
from service import app
from service.my_forms import UserTypeForm, PersonalForm, CompanyForm, AddressForm, TelForm, CompanyTelForm, TermsForm, ReCaptchaForm
import requests
import json
from hurry.filesize import size, alternative
import datetime

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
    if usertype_form.validate_on_submit():
        return redirect(url_for("personal"))
    return user_type(usertype_form)

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
        return redirect(url_for("address"))
    return personal(personal_form)

@app.route('/address')
def address(address_form=None):
    if address_form is None:
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
        return redirect(url_for("tel"))
    return address(address_form)

@app.route('/tel')
def tel(tel_form=None):
    if tel_form is None:
        if 'user_type' not in session:
            return redirect(url_for('user_type'))
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
        return redirect(url_for('recaptcha'))
    return tel(tel_form)

@app.route('/recaptcha')
def recaptcha(recaptcha_form=None):
    if recaptcha_form is None:
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
    print(recaptcha_form.captcha)
    if recaptcha_form.validate_on_submit():
        print("pass")
        session['recaptcha_result'] = 'pass'
        return redirect(url_for('terms'))
    session['recaptcha_result'] = 'fail'
    print("fail")
    return recaptcha(recaptcha_form)

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

@app.route('/printable_terms')
def printable_terms():
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms_printer_friendly.html', text=data)

@app.route('/data', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        session['terms_accepted'] = True
        response = requests.get(app.config['OVERSEAS_OWNERSHIP_URL'] +
                                "/list-files/overseas-ownership")

        ip_address = request.remote_addr

        # Get the link
        files = response.json()['File_List']

        full_datasets = []
        updated_datasets = []

        for link in files:
            # Split into a list of words and reorder the month and year
            words = link["Name"].split("_")
            # Display the month in name format
            words[3] = MONTHS[int(words[3][:2])-1]

            if words[1] == "FULL":
                new_link = "Overseas Dataset (" + words[3] + " " + words[2] + ")"
                full_datasets.append({"filename": new_link, "url": link["URL"],
                                      "size": size(link["Size"], system=alternative)})
            else:
                update_link = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
                updated_datasets.append({"filename": update_link, "url": link["URL"],
                                         "size": size(link["Size"], system=alternative)})

        duration = response.json()['Link_Duration']

        return render_template('data.html', fullDatasets=full_datasets,
                               updatedDatasets=updated_datasets, duration=duration)
    else:
        return redirect(url_for('terms'))

def populate_form(form):
    for field in form:
        if field.name != 'csrf_token' and field.name in session and session[field.name] is not None:
            field.data = session[field.name].strip() if isinstance(session[field.name], str) else session[field.name]

def populate_session(form):
    for field in form:
        if field.name != 'csrf_token' and field.data != 'None' and field.data is not None:
            session[field.name] = field.data.strip() if isinstance(field.data, str) else field.data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
