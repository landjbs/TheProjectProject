import re
import sys
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory
from wtforms import (TextField, StringField, PasswordField, BooleanField,
                    SelectMultipleField, SelectField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)


sys.path.append('.')

from application import db
from application.models import User, Subject


BaseForm = model_form_factory(FlaskForm)
# query all subjects
subjects = [(str(s.id), s.name) for s in db.session.query(Subject)]


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
                                   choices=list(subjects))
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


class Edit_User(BaseForm):
    # name
    name = StringField('Name', validators=[DataRequired(), Length(1, 254)],
                       render_kw={'max':254})
    # email
    email = StringField('New Email',
                    validators=[DataRequired(), Length(1, 254), Email()],
                    render_kw={'max':254})
    # github
    github = StringField('Github',
                    validators=[Length(0, 254), Site_URL_Validator('github')],
                    render_kw={'max':254})
    # password
    password = PasswordField('New Password',
                             validators=[Length(0, 254),
                                         EqualTo('confirm')],
                             render_kw={'max':254})
    # confirm
    confirm = PasswordField('Confirm New Password',
                            validators=[DataRequired()],
                            render_kw={'max':254})




class Login(BaseForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254),
                                             Email(), Email_Ext_Validator()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(1, 254)])


class Add_Project(BaseForm):
    name = StringField(label='Project Name',
                       validators=[DataRequired(), Length(1, 25)],
                       description='Give your project a name!',
                       render_kw={'placeholder':'TheProjectProject',
                                  'max': 25})
    oneliner = StringField(label='One-Liner',
                           validators=[DataRequired(), Length(1, 40)],
                           description='One line description of your project.',
                           render_kw={'placeholder':'Project building community.',
                                      'max': 40})
    summary = TextAreaField(label='Summary',
                        validators=[DataRequired(), Length(1, 400)],
                        description='Describe your project in more detail.',
                        render_kw={'placeholder': ('I need help designing this '
                                                   'online community of '
                                                   'builders...'),
                                  'max':400})
    url = StringField(label='URL',
                    validators=[Length(0, 128)],
                    description=('You can link media (eg. a Github, website, '
                                 'doc, etc.) to showcase your progress.'),
                    render_kw={'placeholder':'https://www.github.com/me/example', 'max':128})
    subjects = SelectMultipleField('Subjects',
                                   description=('What subjects might this '
                                                'project involve?'),
                                   choices=list(subjects))
    open = BooleanField('Open',
                        validators=[],
                        description=('Open projects can have team members.'))
    requires_application = BooleanField('Requires Application',
                            validators=[],
                            description=('Applications allow you to choose '
                                         'who joins the project.'))
    application_question = TextField('Application Question',
                                validators=[Length(0, 128)],
                                description=('Add a question to screen '
                                            'applicants.'),
                                render_kw={'placeholder':'What do you look for in a team?',
                                           'max':128})
    estimated_time = FloatField('Estimated Time',
                                  description=('How long you '
                                  'think the project might take.'),
                                  render_kw={'min':0, 'max':30, 'start':7})
    team_size = IntegerField('Max Team Size',
                            description=('The biggest you want your '
                                         'team to be.'),
                            render_kw={'min':1, 'max':30, 'start':7})
    complete = BooleanField('Completed',
                            description=('Whether the project has been '
                            'completed.'))


class Project_Application_Form(BaseForm):
    # if joining
    response = TextField('Response', validators=[Length(0,250)],
                         render_kw={'max':250})
    # if leaving and owner
    # new_owner = SelectField('Owner', coerce=int)


class Task_Form(BaseForm):
    text = TextField('Task', validators=[DataRequired(), Length(1,160)],
                     render_kw={'max':160})


class Comment_Form(BaseForm):
    text = TextField('Comment', validators=[DataRequired(), Length(1,160)],
                     render_kw={'max':160})
