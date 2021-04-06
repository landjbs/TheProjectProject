import time
import arrow
import click
import requests
from flask import Flask, g, render_template, request, flash
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
import timeago
from dateutil import tz
from datetime import datetime

# config
from app import config
# blueprints
from app.add import add
from app.auth import auth
from app.base import base
from app.competition import competition
from app.hub import hub
from app.user import user
from app.project import project
from app.subject import subject
from app.notification import notification
from app.message import message
from app.badge import badge
from app.question import question
from app.link import link
from app.analytics import analytics
from app.company import company
# database
from app.database import db
# login
from app.user.models import Anonymous
from app.user.forms import Edit_User
# forms
from app.hub.forms import SearchForm
from app.project.forms import Project_Application_Form
from app.message.forms import Message_Form
# models
from app.subject.models import Subject
# extensions
import app.extensions as extensions
# sentry
from app.sentry import register_sentry
# utils
from app.utils import url_for_other_page, partition_query
# commands
from app.commands import command_list

# follow: https://stackoverflow.com/questions/50070979/wrong-dashboard-while-adding-flask-admin-to-project/50179126#50179126


def create_app(config=config.dev_config, register_admin=True):
    ''' Create app and register all extensions and blueprints '''
    application = Flask(
        __name__, static_folder='static', static_url_path='/',
        instance_relative_config=True
    )
    application.config.from_object(config())
    application.url_map.strict_slashes = False
    register_extensions(application)
    register_blueprints(application)
    if register_admin:
        register_admin_views(application, extensions.admin, db)
    register_errorhandlers(application)
    register_jinja_env(application)
    register_commands(application)
    register_sentry(application.config['SENTRY_DSN'])
    # register_elasticsearch(application)

    @application.before_request
    def before_app_request():
        ''' Prepare to handle request '''
        g.request_start_time = time.time()
        # authenticated only
        g.current_user = current_user
        if current_user.is_authenticated:
            current_user.update_last_active()
            g.search_form = SearchForm()
            g.project_application = Project_Application_Form()
            g.message_form = Message_Form()
            g.notifications = current_user.notifications_to_show()
        g.now = datetime.utcnow
        g.request_time = lambda: '%.5fs' % (time.time() - g.request_start_time)
        g.pjax = 'X-PJAX' in request.headers

    # jinja filters
    @application.template_filter('ago')
    def ago(time):
        return timeago.format(time, datetime.utcnow())

    @application.template_filter('time_to_str_new')
    def time_to_str(time):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        time = time.replace(tzinfo=from_zone).astimezone(to_zone)
        return time.strftime('%I:%M %p | %b %d, %Y').lstrip("0").replace(" 0", " ")

    # jinja functions
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
        def now():
            return datetime.utcnow()
        def smallest(x, y):
            return min(x, y)
        return dict(calc_days_since=calc_days_since, calc_days_left=calc_days_left,
                    elapsed_style=elapsed_style, now=now,
                    smallest=smallest)

    # shell
    @application.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}

    return application


def register_extensions(app):
    extensions.csrf.init_app(app)
    extensions.admin.init_app(app)
    extensions.travis.init_app(app)
    extensions.babel.init_app(app)
    extensions.bcrypt.init_app(app)
    extensions.assets.init_app(app)
    extensions.rq.init_app(app)
    extensions.migrate.init_app(app, db)
    extensions.mobility.init_app(app)
    extensions.limiter.init_app(app)
    extensions.serializer.init_app(app)
    extensions.jsglue.init_app(app)
    ######### LOGIN MANAGER #########
    extensions.lm.init_app(app)
    extensions.lm.login_view = 'auth.login'
    extensions.lm.anonymous_user = Anonymous
    ## autolog needs work but the goal is to not have to relogin every restart
    # if not app.config['AUTOLOG']:
    #     extensions.lm.login_view = 'auth.login'
    #     extensions.lm.anonymous_user = Anonymous
    # else:
    #     from app.user.models import User
    #     extensions.lm.anonymous_user = (lambda: User.get_by_id(0))()
    ################################
    db.init_app(app)


def register_blueprints(app):
    ''' Registers all blueprints with application '''
    app.register_blueprint(base)
    app.register_blueprint(auth)
    app.register_blueprint(analytics)
    app.register_blueprint(hub)
    app.register_blueprint(user)
    app.register_blueprint(project)
    app.register_blueprint(add)
    app.register_blueprint(subject)
    app.register_blueprint(notification)
    app.register_blueprint(message)
    app.register_blueprint(badge)
    app.register_blueprint(link)
    app.register_blueprint(competition)
    app.register_blueprint(company)


def register_admin_views(application, admin, db):
    from flask import url_for
    from flask_admin.menu import MenuLink
    # import models
    from app.user.models import User, User_Report
    from app.project.models import Project, Project_Application, Comment, Task
    from app.company.models import Company
    from app.subject.models import Subject, User_Subjects
    from app.notification.models import Notification
    from app.competition.models import Competition, Submission
    from app.analytics.models import PageView
    from app.badge.models import Badge
    from app.message.models import Channel, Message
    # from app.company.models import Company
    # import view
    from app.admin.views import (
        SafeBaseView, SafeModelView, AnalyticsView, UserModelView,
        ReportModelView, CompetitionModelView, SubmissionModelView,
        ProjectModelView
    )
    with application.test_request_context('theprojectproject.io'):
        admin.add_view(AnalyticsView('Analytics', endpoint='AdminAnalytics'))
        admin.add_view(UserModelView(User, db.session, endpoint='AdminUser'))
        admin.add_view(ProjectModelView(Project, db.session, endpoint='AdminProject'))
        admin.add_view(SafeModelView(Company, db.session, endpoint='AdminCompany'))
        admin.add_view(SafeModelView(Comment, db.session, endpoint='AdminComment'))
        admin.add_view(SafeModelView(Task, db.session, endpoint='AdminTask'))
        admin.add_view(SafeModelView(Subject, db.session, endpoint='AdminSubject'))
        admin.add_view(SafeModelView(User_Subjects, db.session, endpoint='AdminUserSubject'))
        admin.add_view(ReportModelView(User_Report, db.session, endpoint='AdminReport'))
        admin.add_view(SafeModelView(Project_Application, db.session, endpoint='AdminApplication'))
        admin.add_view(SafeModelView(Notification, db.session, endpoint='AdminNotification'))
        admin.add_view(SafeModelView(Channel, db.session, endpoint='ChannelNotification'))
        admin.add_view(SafeModelView(Message, db.session, endpoint='AdminMessageView'))
        admin.add_view(CompetitionModelView(Competition, db.session, endpoint='AdminCompetition'))
        admin.add_view(SubmissionModelView(Submission, db.session, endpoint='AdminSubmission'))
        admin.add_view(SafeModelView(Badge, db.session, endpoint='AdminBadge'))
        admin.add_view(SafeModelView(PageView, db.session, endpoint='AdminPageView'))
        # admin.add_view(SafeModelView(Company, db.session, endpoint='AdminCompany'))
        admin.add_link(MenuLink(name='Home', url=url_for('hub.home'), category='Links'))
        admin.add_link(MenuLink(name='Logout', url=url_for('auth.logout'), category='Links'))
    return True


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

    # register handler for bad token
    # from flask_wtf.csrf import CSRFError
    # @app.errorhandler(CSRFError)
    # def handle_csrf_error(e):
    #     return render_template('csrf_error.html', reason=e.description), 400


def register_jinja_env(app):
    """Configure the Jinja env to enable some functions in templates."""
    app.jinja_env.globals.update({
        'timeago': lambda x: arrow.get(x).humanize(),
        'url_for_other_page': url_for_other_page,
        'partition_query': partition_querycool
    })


def register_commands(app):
    """Register custom commands for the Flask CLI."""
    for command in command_list:
        app.cli.command()(command)


def register_elasticsearch(app):
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL']) \
                            if app.config['ELASTICSEARCH_URL'] else None
