from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session, abort)
from gettext import ngettext
from flask_login import current_user
from flask_admin import expose, BaseView
from flask_admin.actions import action
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

from app.jobs import send_acceptance_email

import app.assoc as assoc
from app.user.models import User, User_Report
from app.project.models import Project, Project_Application, Task, Comment
from app.subject.models import Subject
from app.notification.models import Notification
from app.badge.models import Badge, User_Badge
from app.competition.models import Competition
from app.analytics.models import PageView


class SafeView(object):
    ''' Base class for generating safe view children of admin stock classes '''
    def is_accessible(self):
        return (current_user.is_admin())

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('login', next=request.url))


class SafeBaseView(BaseView, SafeView):
    def __init__(self, *args, **kwargs):
        super(SafeBaseView, self).__init__(*args, **kwargs)


class SafeModelView(ModelView, SafeView):
    def __init__(self, *args, **kwargs):
        super(SafeModelView, self).__init__(*args, **kwargs)


class AnalyticsView(SafeBaseView):
    @expose('/')
    def index(self, **kwargs):
        view_data = {}
        view_data['view_count'] = PageView.view_count(past_days=7)
        view_data['user_count'] = PageView.user_count(past_days=7)
        return self.render('admin/analytics.html', view_data=view_data)


class UserModelView(SafeModelView):
    ''' admin view for user model '''
    column_exclude_list = ['password']
    can_export = True
    column_extra_row_actions = [
        EndpointLinkRowAction('glyphicon glyphicon-ok', 'AdminUser.accept_single'),
        EndpointLinkRowAction('glyphicon glyphicon-remove', 'AdminUser.reject_single')
    ]

    @expose('/action/accept_single', methods=('GET',))
    def accept_single(self):
        user = User.query.get_or_404(int(request.args.get('id')))
        send_acceptance_email(user)
        user.accept()
        flash(f'You have accepted {user.name}.')
        return redirect(request.referrer)

    @expose('/action/reject_single', methods=('GET',))
    def reject_single(self):
        user = User.query.get_or_404(int(request.args.get('id')))
        user.reject()
        flash(f'You have rejected {user.name}.')
        return redirect(request.referrer)


    @action('accept', 'Accept', 'Are you sure you want to accept the selected users?')
    def action_accept(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
            count = 0
            for user in query.all():
                if user.accept():
                    send_acceptance_email(user)
                    count += 1

            flash(ngettext('User was successfully accepted.',
                           f'{count} users were successfully accepted.',
                           count))

        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash(gettext('Failed to accept users. %(error)s', error=str(ex)), 'error')


    @action('reject', 'Reject', 'Are you sure you want to reject the selected users?')
    def reject_accept(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
            count = 0
            for user in query.all():
                if user.reject():
                    count += 1

            flash(ngettext('User was successfully rejected.',
                           f'{count} users were successfully rejected.',
                           count))

        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash(gettext('Failed to reject users. %(error)s', error=str(ex)), 'error')


class ReportModelView(SafeModelView):
    ''' admin view for user reports '''
    column_extra_row_actions = [
        EndpointLinkRowAction('glyphicon glyphicon-screenshot', 'user_report.resolve_report')
    ]

    @expose('/action/resolve_report', methods=('GET',))
    def resolve_report(self):
        report = User_Report.query.get_or_404(int(request.args.get('id')))
        return redirect(request.referrer)



def register_admin_views(admin, db):
    # model views
    admin.add_view(AnalyticsView('Analytics'))
    admin.add_view(UserModelView(User, db.session, endpoint='AdminUser'))
    admin.add_view(SafeModelView(Project, db.session, endpoint='AdminProject'))
    admin.add_view(SafeModelView(Comment, db.session, endpoint='AdminComment'))
    admin.add_view(SafeModelView(Task, db.session, endpoint='AdminTask'))
    admin.add_view(SafeModelView(Subject, db.session, endpoint='AdminSubject'))
    admin.add_view(ReportModelView(User_Report, db.session))
    admin.add_view(SafeModelView(Project_Application, db.session, endpoint='AdminApplication'))
    admin.add_view(SafeModelView(Notification, db.session, endpoint='AdminNotification'))
    admin.add_view(SafeModelView(Competition, db.session, endpoint='AdminCompetition'))
    admin.add_view(SafeModelView(PageView, db.session, endpoint='AdminPageView'))
    # nav links
    # admin.add_link(MenuLink(name='Home', url=url_for('hub.home'), category='Links'))
    # admin.add_link(MenuLink(name='Logout', url=url_for('auth.logout'), category='Links'))
    return admin
