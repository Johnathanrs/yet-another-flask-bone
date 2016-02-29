from flask import Flask

from easybiodata.config import config
from easybiodata.core import db
from easybiodata.utils.logging import setup_app_logging, setup_sqlalchemy_debug_logging


def create_app(package_name, config_name):
    app = Flask(package_name)
    app.config.from_object(config[config_name])

    setup_app_logging(app)
    app.logger.info('Using config: {}'.format(config_name))

    db.init_app(app)
    setup_sqlalchemy_debug_logging(app)

    if app.debug:
        _set_cors_headers(app)

    return app


def _set_cors_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3333')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE,GET,HEAD,PATCH,POST,PUT')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        response.headers.add('Vary', 'Origin')
        return response
