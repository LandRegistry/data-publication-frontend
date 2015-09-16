#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for, request
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

@app.route('/terms')
def terms():
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms.html', text=data)

@app.route('/printable_terms')
def printable_terms():
    f = open(app.config['OVERSEAS_TERMS_FILE'], 'r')
    data = f.read()
    f.close()
    return render_template('terms_printer_friendly.html', text=data)

@app.route('/data', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
