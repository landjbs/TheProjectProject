import re
import sys
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory
from wtforms import (TextField, StringField, PasswordField, BooleanField,
                    SelectMultipleField, SelectField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from app.user.models import User
from app.forms.base import BaseForm
from app.forms.validators import


class Edit_User(BaseForm):
    # name
    name = StringField('Name', validators=[DataRequired(), Length(1, 254)],
                       render_kw={'max':254})
    # url
    url = StringField('url',
                    validators=[Length(0, 254)],
                    render_kw={'max':254})
    about = TextField('About You', validators=[DataRequired(), Length(1, 500)],
                      render_kw={'max':500})
    # password
    password = PasswordField('New Password',
                             validators=[Length(0, 254),
                                         EqualTo('confirm')],
                             render_kw={'max':254})
    # confirm
    confirm = PasswordField('Confirm New Password',
                            render_kw={'max':254})
