#!/usr/bin/env python
from flask import abort, render_template, url_for, send_file, request, redirect
from service import app
from random import randint
import requests

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('ood.html')

@app.route('/recaptcha')
@app.route('/recaptcha.htm')
@app.route('/recaptcha.html')
def recaptcha():
    return render_template('recaptcha.html')

@app.route('/data', methods=['POST'])
@app.route('/data.html', methods=['POST'])
def data():
    payload = {'secret': '6LegMQwTAAAAAEhlqMetreZndcUni7Sferq-4q1u', 'response': request.form['g-recaptcha-response']}
    captcha = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    print(captcha.json())
    if captcha.json()['success']:
        response = requests.get('http://localhost:5001/list-files/overseas-ownership')
        files = response.json()['File_List']
        fullDatasets  = []
        updatedDatasets = []

        for link in files:
            # Split into a list of words and reorder the month and year
            words = link["Name"].split("_")
            # Display the month in name format
            words[3] = months[int(words[3][:2])-1]

            if words[1] == "FULL":
                newLink = "Overseas Dataset (" + words[3] + " " + words[2] + ")"
                fullDatasets.append({"filename":newLink, "url":link["URL"]})
            else:
                updateLink = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
                updatedDatasets.append({"filename":updateLink, "url":link["URL"]})

        return render_template('data.html', fullDatasets=fullDatasets, updatedDatasets=updatedDatasets, duration=response.json()['Link_Duration'])
    else:
        error = "Failed reCAPTCHA challenge"
        return render_template('recaptcha.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
