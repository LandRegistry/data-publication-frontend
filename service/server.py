#!/usr/bin/env python
from flask import render_template, request
from service import app
import requests

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

RECAPTCHA_SECRET_KEY = app.config['RECAPTCHA_SECRET_KEY']


@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('ood.html')


@app.route('/recaptcha')
def recaptcha():
    return render_template('recaptcha.html')


@app.route('/data', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        recaptcha_response = ''
    else:
        recaptcha_response = request.form['g-recaptcha-response']

    payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
    captcha = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)

    if captcha.json()['success']:
        response = requests.get('http://localhost:5001/list-files/overseas-ownership')
        files = response.json()['File_List']
        full_datasets = []
        updated_datasets = []

        for link in files:
            # Split into a list of words and reorder the month and year
            words = link["Name"].split("_")
            # Display the month in name format
            words[3] = months[int(words[3][:2])-1]

            if words[1] == "FULL":
                new_link = "Overseas Dataset (" + words[3] + " " + words[2] + ")"
                full_datasets.append({"filename": new_link, "url": link["URL"]})
            else:
                update_link = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
                updated_datasets.append({"filename": update_link, "url": link["URL"]})

        form_data = {'full_datasets': full_datasets,
                     'updated_datasets': updated_datasets,
                     'duration': response.json()['Link_Duration']}
        return render_template('data.html', data=form_data)
    else:
        error = "Failed reCAPTCHA challenge"
        return render_template('recaptcha.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
