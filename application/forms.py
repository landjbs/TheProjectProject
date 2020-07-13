import re
from flask_wtf import FlaskForm
from wtforms import (TextField, StringField, PasswordField, BooleanField,
                    SelectMultipleField, FloatField, validators)
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
                    validators=[DataRequired(), Length(1, 254)],
                    render_kw={'placeholder': 'John Harvard'})
    email = StringField('Harvard Email',
                    validators=[DataRequired(), Length(1, 254),
                                   Email(), Email_Ext_Validator()],
                    description=('Currently only Harvard College emails '
                                   'are allowed. Please reach out if you would '
                                   'like your school to be added.'),
                    render_kw={'placeholder': 'example@college.harvard.edu'})
    github = StringField('Github',
                    validators=[DataRequired(), Length(1, 254),
                                  Site_URL_Validator('github')],
                    description=("Show off past projects on your github if "
                                   "you'd like!"),
                    render_kw={'placeholder': 'https://www.github.com/example'})
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
    accept_terms = BooleanField('I have read and accept the terms.',
                                validators=[DataRequired()],
                            render_kw={'placeholder': 'Yes'})


class Login(BaseForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254),
                                             Email(), Email_Ext_Validator()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(1, 254)])


class Add_Project(BaseForm):
    name = StringField(label='Name',
                       validators=[DataRequired(), Length(1, 128)],
                       render_kw={'placeholder':''})
    summary = TextField(label='Summary',
                        validators=[DataRequired(), Length(1, 500)],
                        description='Give a brief rundown of your idea.',
                        render_kw={'placeholder':''})
    url = StringField(label='Summary',
                    validators=[DataRequired(), Length(1, 128)],
                    description=('You can link media like a Github or website.'
                                 'to showcase your progress.'),
                    render_kw={'placeholder':''})
    # subjects = # TODO:
    open = BooleanField('Open',
                        validators=[DataRequired()],
                        description=('All projects are visible to the '
                            'community, but only open projects can '
                            'be joined by other members.'))
    requires_application = BooleanField('Requires Application',
                            validators=[DataRequired()],
                            description=('If you want to be able to choose '
                            'who can join your project, select this field. '
                            'If not, anyone will be able to join.'))
    application_question = TextField('Application Question',
                                validators=[DataRequired(), Length(1, 250)],
                                description=('To help screen project '
                                    'applicants, you can ask a question. '
                                    'You will be able to see the answer of '
                                    'anyone who works with you.'),
                                render_kw={'placeholder':''})
    estimated_time = FloatField('Estimated Time',
                                description=('Suggest how long you '
                                'think the project might take. This is neither '
                                'binding nor required.'))
    complete = BooleanField('Completed',
                            validators=[DataRequired()],
                            description=('Whether the project has been '
                            'completed.'))
