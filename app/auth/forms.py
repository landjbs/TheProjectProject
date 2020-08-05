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


BaseForm = model_form_factory(FlaskForm)


class Email_Ext_Validator(object):
    ''' Validator for allowed email extensions '''
    def __init__(self, allowed=['college.harvard.edu']):
        self.allowed = set(allowed)

    def __call__(self, form, field):
        # return True
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


class Select_Limit_Validator(object):
    def __init__(self, max):
        self.max = max

    def __call__(self, form, field):
        if len(field.data)>self.max:
            raise ValidationError(f'Must select no more than {self.max} options.')


## FORMS ##
class Apply(BaseForm):
    name = StringField('Name',
                    validators=[DataRequired(), Length(1, 254)],
                    render_kw={'placeholder': 'John Harvard'})
    email = StringField('Harvard Email',
                    validators=[DataRequired(), Length(1, 254),
                                   Email()], # Email_Ext_Validator()
                    description=('Currently only Harvard College emails '
                                   'are allowed. Please reach out if you would '
                                   'like your school to be added.'),
                    render_kw={'placeholder': 'example@college.harvard.edu'})
    github = StringField('Github',
                    validators=[Length(0, 254),
                                  Site_URL_Validator('github')],
                    description=("Show off past projects on your github if "
                                   "you'd like!"),
                    render_kw={'placeholder': 'https://www.github.com/example'})
    about = TextField('About You',
                    validators=[DataRequired(), Length(1, 500)],
                    description=('Describe yourself! This might include '
                               'projects you have worked on, passions you '
                               'have, or reasons you want to join the '
                               'community.'))
    subjects = SelectMultipleField('Interests',
                                    description=('What subjects are you '
                                                'interested in?'),
                                    validators=[Select_Limit_Validator(5)],
                                    choices=[], #list(subjects),
                                    render_kw={'max':5})
    password = PasswordField('Create Password',
                             validators=[DataRequired(), Length(1, 254),
                                         EqualTo('confirm')],
                             description=('Create a password to use if you are '
                                          'accepted.'))
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired()])
    accept_terms = BooleanField('I have read and accept the terms.',
                                validators=[DataRequired()],
                            render_kw={'placeholder': 'Yes'})


class Login(BaseForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254),
                                             Email()])
    password = PasswordField('Password',
                             validators=[Length(0, 254)])

    def validate(self):
        ''' Validates login on all accounts '''
        # stock validation
        rv = BaseForm.validate(self)
        if not rv:
            return False
        # query user
        self.user = User.query.filter_by(email=self.email.data).first()
        # email validation
        if not self.user:
            self.email.errors.append('Email not found.')
            return False
        # password validation
        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password.')
            return False
        # email confirmed validation
        if not self.user.confirmed:
            self.email.errors.append('You have not confirmed your email '
                                     'address. Please check your email for '
                                     'a confirmation link.')
            return False
        if not self.user.accepted:
            self.email.errors.append('Your application is under review—'
                                     'check back soon!')
            return False
        return True
