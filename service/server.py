#!/usr/bin/env python
from flask import render_template, request
from service import app
import requests
from hurry.filesize import size, alternative

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('ood.html')

@app.route('/usertype')
def usertype():
    return render_template('usertype.html')

@app.route('/personal', methods=['POST'])
def personal():
    selection = request.form['user-group']
    return render_template('personal.html')

@app.route('/tel', methods=['POST'])
def tel():
    errors = ''
    address1error = ''
    countryerror = ''
    address1 = request.form['address-line-1'].strip()
    address2 = request.form['address-line-2'].strip()
    address3 = request.form['address-line-3'].strip()
    city = request.form['city'].strip()
    county = request.form['region'].strip()
    postcode = request.form['postal-code'].strip()
    country = request.form['country'].strip()
    if not address1:
        address1error = "Enter the first line of your address. "
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not country:
        countryerror = "Enter the country."
        errors = "There has been an error - make sure all mandatory fields are complete"

    if not errors:
        return render_template('tel.html')
    else:
        return render_template('address.html', errors=errors, address1error=address1error,
             countryerror=countryerror, address1=address1)

@app.route('/address', methods=['POST'])
def address():
    errors = ''
    usernameerror = ''
    titleerror = ''
    forenameerror = ''
    surnameerror = ''
    dayerror = ''
    montherror = ''
    yearerror = ''
    companyerror = ''
    print('one')
    username = request.form['username'].strip()
    print(username)
    title = request.form['title'].strip()
    print(title)
    forename = request.form['first-name'].strip()
    print(forename)
    surname = request.form['last-name'].strip()
    print(surname)
    day = request.form['day'].strip()
    print(day)
    month = request.form['month'].strip()
    print(month)
    year = request.form['year'].strip()
    print(year)
    company = request.form['company-name'].strip()
    print('two')
    if not username:
        usernameerror = "Enter your username."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not title:
        titleerror = "Enter your title."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not forename:
        forenameerror = "Enter your first name."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not surname:
        surnameerror = "Enter your last name."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not day:
        dayerror = "Enter your day of birth."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not month:
        montherror = "Enter your month of birth."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not year:
        yearerror = "Enter your year of birth."
        errors = "There has been an error - make sure all mandatory fields are complete"
    if not company:
        companyerror = "Enter your company name."
        errors = "There has been an error - make sure all mandatory fields are complete"
        print('three')
    if not errors:
        print('address')
        return render_template('address.html')
    else:
        print('personal')
        return render_template('personal.html', errors=errors)

@app.route('/data', methods=['POST'])
@app.route('/data.html', methods=['POST'])
def get_data():
    errors = ''
    mobile = request.form['mobile'].strip()
    landline = request.form['landline'].strip()
    if not mobile and not landline:
        errors = "Enter a telephone number"
    if not errors:
        response = requests.get(app.config['OVERSEAS_OWNERSHIP_URL'] + '/list-files/overseas-ownership')

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
                full_datasets.append({"filename":new_link, "url":link["URL"], "size": size(link["Size"], system=alternative)})
            else:
                update_link = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
                updated_datasets.append({"filename":update_link, "url":link["URL"], "size": size(link["Size"], system=alternative)})

            duration = response.json()['Link_Duration']
        return render_template(
            'data.html', fullDatasets=full_datasets, updatedDatasets=updated_datasets, duration=duration)
    else:
        return render_template('tel.html', errors=errors)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
