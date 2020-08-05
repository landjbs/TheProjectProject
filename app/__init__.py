import time
import arrow
import requests
from flask import Flask, g, render_template, request
from flask_sqlalchemy import SQLAlchemy

from app import config
# blueprints
from app.base import base
from app.auth import auth
#
from app.database import db
from app.extensions import assets, bcrypt, limiter, lm, migrate, rq, travis, csrf
from app.commands import create_db, drop_db, populate_db, rebuild_db
from app.utils import url_for_other_page


def create_app(config=config.BaseConfig):
    ''' '''
    application = Flask(__name__)
    application.config.from_object(config())
    # TODO: better secret key define in config
    # application.config['SECRET_KEY'] = 'asdlfkjads;lkfj;lk2n34,mbn'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///test.db'
    # print(application.config['DATABASE_URI'])
    register_extensions(application)
    register_blueprints(application)
    register_errorhandlers(application)
    register_jinja_env(application)
    register_commands(application)

    @application.before_request
    def before_request():
        ''' prepare to handle each request '''
        g.request_start_time = time.time()
        g.request_time = lambda: '%.5fs' % (time.time() - g.request_start_time)
        g.pjax = 'X-PJAX' in request.headers

    return application


def register_extensions(app):
    csrf.init_app(app)
    travis.init_app(app)
    db.init_app(app)
    lm.init_app(app)
    # mail.init_app(app)
    bcrypt.init_app(app)
    assets.init_app(app)
    # babel.init_app(app)
    rq.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)


def register_blueprints(app):
    ''' Registers all blueprints with application '''
    app.register_blueprint(base)
    app.register_blueprint(auth)


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
        'url_for_other_page': url_for_other_page,
    })


def register_commands(app):
    """Register custom commands for the Flask CLI."""
    for command in [create_db, drop_db, populate_db, rebuild_db]:
        app.cli.command()(command)
