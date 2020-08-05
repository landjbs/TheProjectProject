from flask import Blueprint

auth = Blueprint('admin', __name__, template_folder='templates')

from . import views
