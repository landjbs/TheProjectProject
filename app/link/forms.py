from wtforms import (TextField, StringField, BooleanField,
                    SelectMultipleField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from app.forms.base import BaseForm
from app.forms.validators import Link_Validator


class Add_Link(BaseForm):
    link = StringField(
        label='Link',
        validators=[DataRequired(), Length(1,500), Link_Validator()],
    )
