from flask_wtf import FlaskForm, Form
from wtforms import TextField, validators
from wtforms_alchemy import model_form_factory
from wtforms.validators import (DataRequired, Length, Email, EqualTo,
                                InputRequired, ValidationError, NumberRange)

from .models import Data, User


BaseForm = model_form_factory(FlaskForm)


class EnterDBInfo(BaseForm):
    class Meta:
        model = Data
        validators = {'name': [DataRequired()],
                      # 'email': [DataRequired(), Length(min=1, max=254)], #Email(),
                      'password': [DataRequired(), Length(min=1, max=254)]}


class Apply(BaseForm):
    class Meta:
        model = User
        validators = {'name': [DataRequired()],
                     # 'email': [DataRequired(), Email(), Length(min=1, max=254)],
                     'password': [DataRequired(), Length(min=1, max=254)]}

# class EnterDBInfo(Form):
#     dbNotes = TextField(label='Items to add to DB', description="db_enter", validators=[validators.required(), validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])
#     password = TextField(label='Items to add to DB', description="db_enter", validators=[validators.required(), validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])

class RetrieveDBInfo(Form):
    numRetrieve = TextField(label='Number of DB Items to Get', description="db_get", validators=[validators.required(), validators.Regexp('^\d{1}$',message=u'Enter a number between 1 and 10')])
