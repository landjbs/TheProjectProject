import re
from flask_wtf import FlaskForm
from wtforms import TextField, validators, PasswordField
from wtforms_alchemy import model_form_factory
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from .models import Data, User


BaseForm = model_form_factory(FlaskForm)


class Email_Ext_Validator(object):
    ''' Validator for allowed email extensions '''
    def __init__(self, allowed=['college.harvard.edu']):
        self.allowed = set(allowed)

    def __call__(self, form, field):
        email = str(field.data)
        ending = email.split('@')[-1]
        print(ending)
        if not ending in self.allowed:
            raise ValidationError('Currently only Harvard College emails '
                                  'are allowed.')


class Site_URL_Validator(object):
    ''' Validator for http or https URLs from site '''
    def __init__(self, site):
        self.site = site
        matcher = (r'(www\.|http://|https://|http://www\.|https://\.)'
                   f'{site}.com/'
                   r'.*')
        self.matcher = re.compile(matcher)

    def __call__(self, form, field):
        if not re.match(self.matcher, field.data):
            raise ValidationError(f"Invalid URL for {self.site}.")


class Apply(BaseForm):
    class Meta:
        model = User
        exclude = ['status']
        validators = {'name': [],
                      'email': [Email(), Email_Ext_Validator(),
                                Length(min=1, max=254)],
                      'password': [Length(min=1, max=254)],
                      'confirm': [],
                      'github': [Site_URL_Validator('github')],
                      'about': []}
        # all fields are required
        for k, v in validators.items():
            v.append(DataRequired())


class Login(BaseForm):
    class Meta:
        model = User
        only = ['email', 'password']
