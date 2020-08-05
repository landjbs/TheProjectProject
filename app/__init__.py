import time
import requests
from flask import Flask, g, render_template, request
from flask_sqlalchemy import SQLAlchemy
from app.extensions import register_extensions
from app.commands import create_db, drop_db, populate_db, recreate_db
from app.utils import url_for_other_page


def create_app(config=config.base_config):
    ''' '''
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_errorhandlers(app)
    register_jinja_env(app)
    register_commands(app)

    @app.before_request
    def before_request():
        ''' prepare to handle each request '''
        g.request_start_time = time.time()
        g.request_time = lambda: '%.5fs' % (time.time() - g.request_start_time)
        g.pjax = 'X-PJAX' in request.headers

    @application.route('/', methods=['GET'])
    @application.route('/index', methods=['GET'])
    def index():
        return render_template('index.html')

    return app


def register_errorhandlers(app):
    ''' Registers handlers for all errors '''

    def render_error(e):
        return render_template(f'errors/{e.code}.html'), e.code

    for e in [
        requests.codes.INTERNAL_SERVER_ERROR,
        requests.codes.NOT_FOUND,
        requests.codes.UNAUTHORIZED,
    ]:
        app.errorhandler(e)(render_error)


def register_jinja_env(app):
    """Configure the Jinja env to enable some functions in templates."""
    app.jinja_env.globals.update({
        'timeago': lambda x: arrow.get(x).humanize(),
        # TODO: define url_for_other_page from app.utils
        'url_for_other_page': url_for_other_page,
    })


def register_commands(app):
    """Register custom commands for the Flask CLI."""
    for command in [create_db, drop_db, populate_db, recreate_db]:
        app.cli.command()(command)
