import time
import arrow
import click
import requests
from flask import Flask, g, render_template, request
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from dateutil import tz

# config
from app import config
# blueprints
from app.auth import auth
from app.base import base
from app.competition import competition
from app.hub import hub
from app.user import user
from app.project import project
from app.subject import subject
from app.notification import notification
from app.badge import badge
from app.question import question
from app.link import link
from app.admin import register_admin_views
# database
from app.database import db
# login
from app.user.models import Anonymous
# forms
from app.hub.forms import SearchForm
# extensions
from app.extensions import (assets, admin, bcrypt, csrf, limiter,
                            lm, migrate, rq, travis, babel, mobility)
# utils
from app.utils import url_for_other_page
# commands
from app.commands import command_list


def create_app(config=config.dev_config):
    ''' '''
    application = Flask(__name__, static_folder='static', static_url_path='')
    application.config.from_object(config())
    register_extensions(application)
    register_blueprints(application)
    register_errorhandlers(application)
    register_jinja_env(application)
    register_commands(application)
    register_admin_views(admin, db)
    # register_elasticsearch(application)

    @application.before_request
    def before_app_request():
        ''' prepare to handle each request '''
        g.request_start_time = time.time()
        # authenticated only
        if current_user.is_authenticated:
            g.current_user = current_user
            current_user.update_last_active()
            g.search_form = SearchForm()
        #
        g.now = datetime.utcnow
        g.request_time = lambda: '%.5fs' % (time.time() - g.request_start_time)
        g.pjax = 'X-PJAX' in request.headers

    # TODO: SIMPLIFY CONTEXT PROCESSOR: MOSTLY INTEGRATE INTO AJAX ACCORDING TO FLASK TUTORIAL
    from datetime import datetime
    @application.context_processor
    def utility_processor():
        def calc_days_since(now, start):
            return int((now - start).days)
        def calc_days_left(elapsed, estimated_time):
            if estimated_time:
                return int((estimated_time - elapsed))
            else:
                return 0
        def elapsed_style(elapsed, estimated_time):
            if estimated_time:
                return f'width: {100*float(elapsed/estimated_time)}%;'
            else:
                return f'width: 100%;'
        def time_to_str(time):
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            time = time.replace(tzinfo=from_zone)
            time = time.astimezone(to_zone)
            # time = f"{time.strftime('%B %d, %Y')} at {time.strftime('%I:%M %p')}"
            time = f"{time.strftime('%B %d')}"
            time = time.lstrip("0").replace(" 0", " ")
            return time
        def now():
            return datetime.utcnow()
        return dict(calc_days_since=calc_days_since, calc_days_left=calc_days_left,
                    elapsed_style=elapsed_style, time_to_str=time_to_str, now=now)

    return application


def register_extensions(app):
    csrf.init_app(app)
    admin.init_app(app)
    travis.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    bcrypt.init_app(app)
    assets.init_app(app)
    rq.init_app(app)
    migrate.init_app(app, db)
    mobility.init_app(app)
    limiter.init_app(app)
    ######### LOGIN MANAGER #########
    lm.init_app(app)
    lm.login_view = 'auth.login'
    lm.anonymous_user = Anonymous
    ################################


def register_blueprints(app):
    ''' Registers all blueprints with application '''
    app.register_blueprint(base)
    app.register_blueprint(auth)
    app.register_blueprint(hub)
    app.register_blueprint(user)
    app.register_blueprint(project)
    app.register_blueprint(subject)
    app.register_blueprint(notification)
    app.register_blueprint(badge)
    app.register_blueprint(link)
    app.register_blueprint(competition)


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
    for command in command_list:
        app.cli.command()(command)


def register_elasticsearch(app):
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL']) \
                            if app.config['ELASTICSEARCH_URL'] else None
