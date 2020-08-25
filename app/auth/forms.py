from wtforms import (TextField, StringField, PasswordField, BooleanField,
                    SelectMultipleField, SelectField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email)

from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator
from app.link.utils import fix_url

from app.user.models import User


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
    about = TextField('About You',
                    validators=[DataRequired(), Length(1, 500)],
                    description=('Describe yourself! This might include '
                               'projects you have worked on, passions you '
                               'have, or reasons you want to join the '
                               'community.'))
    subjects = SelectMultipleField('Passions',
                                    description=('What fields are you '
                                                'interested in?'),
                                    validators=[Select_Limit_Validator(5)],
                                    choices=[], coerce=int,
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
        return (not error_flag)


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


class StartReset(BaseForm):
    email = StringField('Harvard Email',
                    validators=[DataRequired(), Length(1, 254),
                                   Email()], # Email_Ext_Validator()
    )
