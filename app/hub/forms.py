from wtforms import (TextField, StringField)
from wtforms.validators import (DataRequired, Length, EqualTo, Email)

from app.user.models import User
from app.forms.base import BaseForm
from app.forms.validators import Site_URL_Validator, Select_Limit_Validator


class SearchForm(BaseForm):
    search = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(Search_Form, self).__init__(*args, **kwargs)
