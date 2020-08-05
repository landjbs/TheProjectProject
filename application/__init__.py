import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from extensions import register_extensions


application = Flask(__name__)
application.config.from_object('config')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)
db.init_app(application)


def create_app(config=config.base_config):
    ''' '''
    app = Flask(__name__, )
    app.config.from_object(config)
    register_extensions(app)
    register_errorhandlers(app)


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
