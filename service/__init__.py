#!/usr/bin/env python
from flask import Flask, request
from flask.ext.assets import Environment, Bundle
from os import path
import sass as libsass
from flask_wtf.csrf import CsrfProtect

from service import error_handler
from config import CONFIG_DICT

app = Flask(__name__)
app.config.update(CONFIG_DICT)
app.secret_key = app.config['SESSION_KEY']
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

@app.context_processor
def inject_user_id():
    return dict(user_id=request.headers.get('iv_user'))
