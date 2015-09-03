#!/usr/bin/env python
from flask import abort, render_template, url_for, send_file, request, redirect
from service import app
from random import randint

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('ood.html')

@app.route('/data')
@app.route('/data.html')
def data():
    response = requests.get['http://localhost:5001/list-files/overseas-ownership']

    # Get the link
    files = response.json['File list']

#    dic1 = {"filename":"ov_full_2015_08.zip","url":"ov_full_2015_08"}
#    dic2 = {"filename":"ov_updates_2014_07.zip","url":"ov_updates_2014_07"}
#    dic3 = {"filename":"ov_updates_2015_09.zip","url":"ov_updates_2015_09"}

#    files.append(dic1)
#    files.append(dic2)
#    files.append(dic3)

    fullDatasets  = []
    updatedDatasets = []


    for link in files:
        # Split into a list of words and reorder the month and year
        words = link["Name"].split("_")
        # Display the month in name format
        words[3] = months[int(words[3][:2])-1]

        print (words)
        if words[1] == "FULL":
            newLink = "Overseas Dataset (" + words[3] + " " + words[2] + ")"
            fullDatasets.append({"filename":newLink, "url":link["url"]})
        else:
            updateLink = "Overseas Dataset (" + words[3] + " " + words[2] + " update)"
            updatedDatasets.append({"filename":updateLink, "url":link["url"]})

    return render_template('data.html', fullDatasets=fullDatasets, updatedDatasets=updatedDatasets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
