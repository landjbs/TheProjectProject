from flask import url_for
from wtforms import (TextField, StringField, BooleanField, SelectField,
                    SelectMultipleField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)
# absolute imports
from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator
from app.link.utils import fix_url
# package imports
from app.project.models import Project
from app.company.models import Company


class Add(BaseForm):
    '''
    Dynamic add form. Currently supports Project and Company
    '''
    ## SHARED FIELDS ##
    name = StringField(label='Project Name',
                       validators=[DataRequired(), Length(1, 40)],
                       description='Give your project a name!',
                       render_kw={'placeholder':'TheProjectProject',
                                  'max': 30})
    oneliner = StringField(label='One-Liner',
                           validators=[DataRequired(), Length(1, 100)],
                           description='One line description of your project.',
                           render_kw={'placeholder':'The platform for sharing, collaborating on, and publicizing independent projects.',
                                      'max': 40})
    summary = TextAreaField(label='Summary',
                        validators=[DataRequired(), Length(1, 400)],
                        description='Describe your project in more detail.',
                        render_kw={'placeholder': ('TheProjectProject is a virtual community of innovators, who collaborate on projects across a wide range of fields and time windows. '
                                                'I need a team of web developers, database experts, and creative minds to help me build this platform. We will tackle interesting problems '
                                                'such as matching users with projects they will like and designing an interface that helps people communicate their ideas...'),
                                  'max':400})
    subjects = SelectMultipleField('Subjects',
                                    description=('What subjects might this '
                                                'project involve?'),
                                    validators=[], choices=[], coerce=int)
    ## PROJECT FIELDS

    ## COMPANY FIELDS
    # funding
    has_raised = BooleanField(
                    label='',
                    validators=[DataRequired(), Length()],
                    description='',
                    render_kw={''}
                )
    amount_raised = IntegerField()
    looking_to_raise = BooleanField()
    # team building
    looking_for_members = BooleanField()
    application_question = StringField()
