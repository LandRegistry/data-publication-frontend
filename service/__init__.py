#!/usr/bin/env python
from flask import Flask, request
from flask.ext.assets import Environment, Bundle
from flask_wtf.csrf import CsrfProtect
from os import path
import sass as libsass

from service import error_handler
from config import CONFIG_DICT

app = Flask(__name__)
app.config.update(CONFIG_DICT)
app.secret_key = app.config['SESSION_KEY']
app.session_cookie_name = 'lr_data_session'
error_handler.setup_errors(app)

CsrfProtect(app)

assets = Environment(app)

__dot = path.dirname(path.realpath(__file__))
__elements_dir = path.join(__dot, 'static/govuk-elements-scss/')
__fronted_toolkit_dir = path.join(__dot, 'static/govuk_frontend_toolkit-scss/')


def __compile_sass(_in, out, **kw):
    out.write(
        libsass.compile(
            string=_in.read(),
            include_paths=[__elements_dir, __fronted_toolkit_dir]
        )
    )


sass = Bundle('govuk-elements-scss/main.scss',
              'govuk-elements-scss/main-ie6.scss',
              'govuk-elements-scss/main-ie7.scss',
              'govuk-elements-scss/main-ie8.scss',
              filters=(__compile_sass,),
              output='build/stylesheets/govuk_sass.css')
assets.register('govuk_sass', sass)


@app.context_processor
def asset_path_context_processor():
    return {
        'asset_path': '/static/build/',
        'landregistry_asset_path': '/static/build/'
    }


GOOGLE_ANALYTICS_PROPERTY_ID = app.config['GOOGLE_ANALYTICS_PROPERTY_ID']

@app.context_processor
def inject_google_analytics():
    return {'ga_property_id': GOOGLE_ANALYTICS_PROPERTY_ID}

URL_PREFIX = app.config['URL_PREFIX']

@app.context_processor
def inject_url_prefix():
    return {'url_prefix': URL_PREFIX}
