from wtforms import (TextField, StringField, PasswordField)
from wtforms.validators import (DataRequired, Length, EqualTo)

from app.user.models import User
from app.forms.base import BaseForm
