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
