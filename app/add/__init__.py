from flask import Blueprint

add = Blueprint('add', __name__, template_folder='templates')

from . import views
