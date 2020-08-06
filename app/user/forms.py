from wtforms import (TextField, StringField, PasswordField)
from wtforms.validators import (DataRequired, Length, EqualTo)

from app.user.models import User
from app.forms.base import BaseForm


# TODO: ADD "AWAY" BOOL TO USERS

class Edit_User(BaseForm):
    # name
    name = StringField('Name', validators=[DataRequired(), Length(1, 254)],
                       render_kw={'max':254})
    # url
    url = StringField('URL', validators=[Length(0, 254)], render_kw={'max':254})
    about = TextField('About', validators=[DataRequired(), Length(1, 500)],
                      render_kw={'max':500})
    # password
    password = PasswordField('New Password',
                             validators=[Length(0, 254), EqualTo('confirm')],
                             render_kw={'max':254})
    # confirm
    confirm = PasswordField('Confirm New Password',
                            render_kw={'max':254})
