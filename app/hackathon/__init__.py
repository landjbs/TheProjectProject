from flask import Blueprint

hackathon = Blueprint('hackathon', __name__, template_folder='templates')

from . import views
