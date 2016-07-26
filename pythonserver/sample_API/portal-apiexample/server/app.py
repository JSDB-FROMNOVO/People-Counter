# -*- coding: utf-8 -*-

import os

from flask import Flask, render_template

from .config import DefaultConfig
from .api import api
from .extensions import db
from flask.ext.cors import CORS
#from vnc_api import vnc_api
from novaclient import client


# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    api,
)


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name,
                instance_relative_config=True)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    # configure_logging(app)
    # configure_template_filters(app)
    # configure_error_handlers(app)

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    app.config.from_object(DefaultConfig)

    app.config.from_pyfile('config.py', silent=True)

    if config:
        app.config.from_object(config)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)
    CORS(app, resources=r'/api/*',
         allow_headers='Content-Type')
    OS_USERNAME = app.config["OS_USERNAME"]
    OS_PASSWORD = app.config["OS_PASSWORD"]
    OS_TENANT_NAME = app.config["OS_TENANT_NAME"]
    #OS_SERVER = app.config["OS_SERVER"]
    AUTH_URL = app.config["OS_AUTH_URL"]
    app.nova = client.Client(2, OS_USERNAME,
                             OS_PASSWORD,
                             OS_TENANT_NAME,
                             auth_url=AUTH_URL)

    #app.vnc_lib = vnc_api.VncApi(username=OS_USERNAME,
    #                             password=OS_PASSWORD,
    #                             tenant_name=OS_TENANT_NAME,
    #                             api_server_host=OS_SERVER)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):

    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(
        info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500
