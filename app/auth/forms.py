from wtforms import (TextField, StringField, PasswordField, BooleanField,
                    SelectMultipleField, SelectField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from app.user.models import User
form app.forms.base import BaseForm
from app.forms.validators import Site_URL_Validator, Select_Limit_Validator


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
    url = StringField('URL',
                    validators=[Length(0, 254)],
                    description=('Tell us about yourself with a Github or '
                                 'personal website!'),
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

    def validate(self):
        ''' Validates application '''
        # error flag to check all errors at once
        error_flag = False
        # stock validation
        rv = BaseForm.validate(self)
        if not rv:
            error_flag = True
        # unique email validation
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('There is already an account registered '
                                     'with that email.')
            error_flag = True
        # unique url validation
        if self.url.data=='':
            self.url.data = None
        if self.url.data:
            user = User.query.filter_by(url=self.url.data).first()
            if user:
                self.url.errors.append('There is already an account '
                                         'registered with that URL.')
                error_flag = True
        if error_flag:
            return False
        return True


class Login(BaseForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254),
                                             Email()])
    password = PasswordField('Password',
                             validators=[Length(0, 254)])

    def validate(self):
        ''' Validates login '''
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
