import re
from flask_wtf import FlaskForm, Form
from wtforms import TextField, validators
from wtforms_alchemy import model_form_factory
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from .models import Data, User


BaseForm = model_form_factory(FlaskForm)


class Email_Ext_Validator(object):
    ''' Validator for allowed email extensions '''
    def __init__(self, allowed=['@college.harvard.edu']):
        self.allowed = set(allowed)

    def __call__(self, form, field):
        email = str(field.data)
        try:
            ending = email.split('@')[-1]
            if not ending in self.allowed:
                raise ValidationError('Currently only Harvard College emails '
                                      'are allowed.')
        except:
            raise ValidationError('Invalid email address.')


class Site_URL_Validator(object):
    ''' Validator for http or https URLs from site '''
    def __init__(self, site):
        matcher = (r'(www\.|http://|https://|http://www\.|https://\.)'
                   f'{site}.com/'
                   r'.*')
        self.matcher = re.compile(matcher)

    def __call__(self, form, field):
        if not re.match(matcher, form.data):
            raise ValidationError(f"Invalid URL for {site}.")



class Apply(BaseForm):
    class Meta:
        model = User
        exclude = ['status']
        validators = {'name': [DataRequired()],
                      'email': [DataRequired(), Email(), Email_Ext_Validator(),
                                Length(min=1, max=254)],
                      'password': [DataRequired(), Length(min=1, max=254)]}


class EnterDBInfo(BaseForm):
    class Meta:
        model = Data
        validators = {'name': [DataRequired()],
                     'password': [DataRequired(), Length(min=1, max=254)]}

# class EnterDBInfo(Form):
#     dbNotes = TextField(label='Items to add to DB', description="db_enter", validators=[validators.required(), validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])
#     password = TextField(label='Items to add to DB', description="db_enter", validators=[validators.required(), validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])

class RetrieveDBInfo(Form):
    numRetrieve = TextField(label='Number of DB Items to Get', description="db_get", validators=[validators.required(), validators.Regexp('^\d{1}$',message=u'Enter a number between 1 and 10')])
