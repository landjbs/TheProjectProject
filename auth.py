from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import application.models as models


class UserView(ModelView):
    @action('approve', 'Approve', 'Are you sure you want to approve the selected users?')
    def action_approve(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
