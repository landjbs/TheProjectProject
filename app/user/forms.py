from wtforms import (TextField, StringField, PasswordField, SelectMultipleField)
from wtforms.validators import (DataRequired, Length, EqualTo)
# absolute imports
from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator
# package imports
from .models import User


# # NOTE: ADD "AWAY" BOOL TO USERS
class Edit_User(BaseForm):
    # name
    name = StringField('Name', validators=[DataRequired(), Length(1, 254)],
                       render_kw={'max':254})
    # about
    about = TextField('Bio', validators=[DataRequired(), Length(1, 500)],
                      render_kw={'max':500})
    # subjects
    subjects = SelectMultipleField('Passions',
                            description=('What are you passionate about?'),
                            validators=[],
                            choices=[],
                            coerce=int
                        )
    # password
    password = PasswordField('New Password',
                             validators=[Length(0, 254), EqualTo('confirm')],
                             render_kw={'max':254})
    # confirm
    confirm = PasswordField('Confirm New Password',
                            render_kw={'max':254})
