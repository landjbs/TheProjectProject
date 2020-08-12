from flask import Blueprint

question = Blueprint('question', __name__, template_folder='templates')

from . import views
