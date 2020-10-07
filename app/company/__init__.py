from flask import Blueprint

company = Blueprint('company', __name__, template_folder='templates')

from . import views
