''' Base form models '''

from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory

BaseForm = model_form_factory(FlaskForm)
