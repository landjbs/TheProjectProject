from gettext import ngettext
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView

import application.models as models
from flask import flash


class UserView(ModelView):
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
    def action_accept(self, ids):
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
