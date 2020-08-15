from flask import Blueprint

competition = Blueprint('competition', __name__, template_folder='templates')

from . import views
