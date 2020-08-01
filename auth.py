from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView

import application.models as models


class UserView(ModelView):
    @action('accept', 'Accept', 'Are you sure you want to accept the selected users?')
    def action_accept(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
            count = 0
            for user in query.all():
                if user.accept():
                    count += 1

            flash(ngettext('User was successfully accepted.',
                           '%(count)s users were successfully accepted.',
                           count,
                           count=count))

        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash(gettext('Failed to accept users. %(error)s', error=str(ex)), 'error')
