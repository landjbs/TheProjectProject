from wtforms import (TextField, StringField, PasswordField, BooleanField,
                    SelectMultipleField, SelectField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email)

from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator, EDU_Validator
from app.link.utils import fix_url

from app.user.models import User


## FORMS ##
class Apply(BaseForm):
    name = StringField(
        label='Name',
        validators=[DataRequired(), Length(1, 254)],
        render_kw={
            'placeholder': 'John Harvard',
            'tabclass':     ''
        }
    )
    email = StringField(
        label='College Email',
        validators=[DataRequired(), Length(1, 254), Email()],
        render_kw={
            'placeholder': 'example@college.harvard.edu',
            'tabclass':     ''
        }
    )
    subjects = SelectMultipleField(
        label='Passions',
        description=('What fields are you interested in?'),
        validators=[],
        choices=[],
        coerce=int,
        render_kw={
            'max':5,
            'tabclass':     ''
        }
    )
    password = PasswordField(
        label='Create Password',
        validators=[DataRequired(), Length(1, 254)],
        description='Create a password!',
        render_kw={
            'tabclass':     ''
        }
    )
    accept_terms = BooleanField(
        label='I have read and accept the terms.',
        validators=[DataRequired()],
        render_kw={
            'placeholder': 'Yes',
            'tabclass':     '',
            'datamap': {
                'true': {
                    'action':   ''
                },
                'false': {
                    'action':   ''
                }
            }
        }
    )

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
    email = StringField('Enter Email to Reset Password',
                    validators=[DataRequired(), Length(1, 254),
                                Email()], # Email_Ext_Validator()
                    render_kw={'placeholder': 'example@college.harvard.edu'}
    )

    def validate(self):
        # stock validation
        rv = BaseForm.validate(self)
        if not rv:
            return False
        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            self.email.errors.append('Email not found.')
            return False
        return True


class PasswordReset(BaseForm):
    password = PasswordField('New Password',
                             validators=[DataRequired(), Length(1, 254),
                                         EqualTo('confirm')],
                             description=(''))
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired()])
