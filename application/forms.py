import re
from flask_wtf import FlaskForm
from wtforms import (TextField, StringField, PasswordField, BooleanField,
                     validators)
from wtforms_alchemy import model_form_factory
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from .models import User


BaseForm = model_form_factory(FlaskForm)


class Email_Ext_Validator(object):
    ''' Validator for allowed email extensions '''
    def __init__(self, allowed=['college.harvard.edu']):
        self.allowed = set(allowed)

    def __call__(self, form, field):
        email = str(field.data)
        ending = email.split('@')[-1]
        if not ending in self.allowed:
            raise ValidationError('Currently only Harvard College emails '
                                  'are allowed.')


class Site_URL_Validator(object):
    ''' Validator for http or https URLs from site '''
    def __init__(self, site):
        self.site = site
        matcher = (r'(www\.|http://|https://|http://www\.|https://\.)'
                   f'{site}.com/'
                   r'.+')
        self.matcher = re.compile(matcher)

    def __call__(self, form, field):
        if not re.match(self.matcher, field.data):
            raise ValidationError(f"Invalid URL for {self.site}.")


class Apply(BaseForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(1, 254)])
    email = StringField('Harvard Email',
                       validators=[DataRequired(), Length(1, 254),
                                   Email(), Email_Ext_Validator()],
                       description=('Currently only Harvard College emails '
                                   'are allowed. Please reach out if you would '
                                   'like your school to be added.'))
    github = StringField('Github',
                      validators=[DataRequired(), Length(1, 254),
                                  Site_URL_Validator('github')],
                      description=("Show off past projects on your github if "
                                   "you'd like!"))
    about = TextField('About',
                      validators=[DataRequired(), Length(1, 500)],
                      description=('Describe yourself! This might include '
                                   'projects you have worked on, passions you '
                                   'have, or reasons you want to join the '
                                   'community.'))
    password = PasswordField('Create Password',
                             validators=[DataRequired(), Length(1, 254),
                                         EqualTo('confirm')],
                             description=('Create a password to use if you are '
                                          'accepted.'))
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired()])
    accept_terms = BooleanField('I accept the terms.',
                                validators=[DataRequired()])


# class Apply(BaseForm):
#     class Meta:
#         model = User
#         exclude = ['accepted']
#         validators = {'name': [],
#                       'email': [Email(), Email_Ext_Validator(),
#                                 Length(min=1, max=254)],
#                       'password': [Length(min=1, max=254)],
#                       'confirm': [],
#                       'github': [Site_URL_Validator('github')],
#                       'about': []}
#         # all fields are required
#         for k, v in validators.items():
#             v.append(DataRequired())


class Login(BaseForm):
    class Meta:
        model = User
        only = ['email', 'password']
