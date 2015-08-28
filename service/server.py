#!/usr/bin/env python
from flask import abort, render_template, url_for, send_file, request, redirect
from service import app
from random import randint

open_datasets = []
commercial_datasets = ['NSD']


@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    return render_template('nsd.html')

@app.route('/data')
@app.route('/data.html')
def data():
    return render_template('data.html')

@app.route('/<data_type>/<dataset>')
def view_commercial_dataset_page(data_type, dataset):

    # Check they are trying to access the datasets via the correct URL e.g. NSD via 'commercial' not 'open'
    check_valid_dataset_type(data_type, dataset)

    # Retrieve the eSecurity values from the request header
    esecurity = get_esecurity_header_values()

    # TEMPORARY
    # If user is trying to access a commercial dataset send them to the login page if no user_id in request header
    if not esecurity["user_id"] and data_type.lower() == 'commercial':
        breadcrumbs = [
            {"text": "Home", "url": url_for('index', _external=True)},
            {"text": "Login", "url": ""}
        ]
        return render_template('login.html', breadcrumbs=breadcrumbs)

    breadcrumbs = [
        {"text": "Home", "url": url_for('index', _external=True)},
        {"text": "Dataset download", "url": ""}
    ]

    x = randint(1, 5)
    roles = esecurity["roles"] if esecurity["roles"] else ''
    return render_template(dataset + ".html", breadcrumbs=breadcrumbs, files=x, roles=roles)


@app.route('/<data_type>/<dataset>/<filename>')
def download_dataset(data_type, dataset, filename):

    # Check they are trying to access the datasets via the correct URL e.g. NSD via 'commercial' not 'open'
    check_valid_dataset_type(data_type, dataset)

    return send_file("static/Datasets/NSD-Dataset-1.zip",
                     mimetype="application/zip",
                     as_attachment=True,
                     attachment_filename=filename)


def check_valid_dataset_type(data_type, dataset):
    if data_type.lower() == 'commercial':
        if dataset.upper() not in commercial_datasets:
            abort(404)
    elif data_type.lower() == 'open':
        if dataset.upper() not in open_datasets:
            abort(404)
    else:
        abort(404)


def get_esecurity_header_values():
    header_info = {
        "user_id": request.headers.get('iv-user'),
        "roles": request.headers.get('iv-groups')
    }
    return header_info


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
