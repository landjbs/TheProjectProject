from flask import Blueprint

hub = Blueprint('hub', __name__, template_folder='templates')

from . import views
