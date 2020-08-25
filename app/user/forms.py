from wtforms import (TextField, StringField, PasswordField, MultipleSelectField)
from wtforms.validators import (DataRequired, Length, EqualTo)
# absolute imports
from app.forms.base import BaseForm
# package imports
from .models import User


# # NOTE: ADD "AWAY" BOOL TO USERS
class Edit_User(BaseForm):
    # name
    name = StringField('Name', validators=[DataRequired(), Length(1, 254)],
                       render_kw={'max':254})
    # about
    about = TextField('About', validators=[DataRequired(), Length(1, 500)],
                      render_kw={'max':500})
    # subjects
    subjects = SelectMultipleField(
                'Subjects',
                description=('What subjects might this '
                            'project involve?'),
                validators=[Select_Limit_Validator(5)],
                choices=[], coerce=int,
                render_kw={'max':5})
    # password
    password = PasswordField('New Password',
                             validators=[Length(0, 254), EqualTo('confirm')],
                             render_kw={'max':254})
    # confirm
    confirm = PasswordField('Confirm New Password',
                            render_kw={'max':254})
