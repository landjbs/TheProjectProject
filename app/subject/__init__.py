from flask import Blueprint

subject = Blueprint('subject', __name__, template_folder='templates')

from . import views
