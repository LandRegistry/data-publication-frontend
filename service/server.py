#!/usr/bin/env python
from flask import render_template
from service import app
import requests

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('ood.html')

@app.route('/data')
@app.route('/data.html')
def get_data():
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
            full_datasets.append({"filename":new_link, "url":link["URL"]})
        else:
            update_link = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
            updated_datasets.append({"filename":update_link, "url":link["URL"]})

    return render_template(
        'data.html', fullDatasets=full_datasets, updatedDatasets=updated_datasets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
