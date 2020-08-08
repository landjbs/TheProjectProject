from flask import Blueprint

badge = Blueprint('badge', __name__, template_folder='templates')

from . import views
