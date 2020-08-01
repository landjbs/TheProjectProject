from gettext import ngettext
from flask_admin import expose
from flask_admin.actions import action
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView

import application.models as models
from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)


class UserView(ModelView):
    ''' admin view for user model '''
    column_exclude_list = ['password']
    can_export = True
    column_extra_row_actions = [
        EndpointLinkRowAction('glyphicon glyphicon-ok', 'user.accept_single')
        EndpointLinkRowAction('glyphicon glyphicon-ok', 'user.reject_single')
        'glyphicon glyphicon-remove'
    ]

    @expose('/action/accept_single', methods=('GET',))
    def accept_single(self):
        user = models.User.query.get_or_404(int(request.args.get('id')))
        user.accept()
        flash(f'You have accepted {user.name}.')
        return redirect(request.referrer)

    @expose('/action/reject_single', methods=('GET',))
    def accept_single(self):
        user = models.User.query.get_or_404(int(request.args.get('id')))
        user.reject()
        flash(f'You have rejected {user.name}.')
        return redirect(request.referrer)


    @action('accept', 'Accept', 'Are you sure you want to accept the selected users?')
    def action_accept(self, ids):
        try:
            query = models.User.query.filter(models.User.id.in_(ids))
            count = 0
            for user in query.all():
                if user.accept():
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
            query = models.User.query.filter(models.User.id.in_(ids))
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


# class ReportView(ModelView):
#     ''' admin view for user reports '''
#     @expose('/')
