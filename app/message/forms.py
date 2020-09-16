from wtforms import TextField

from app.forms.base import BaseForm
from wtforms.validators import DataRequired, Length


class Message_Form(BaseForm):
    ''' Form to message channel '''
    text = TextField('Text', validators=[DataRequired(), Length(1,160)],
                     render_kw={'max':160})
