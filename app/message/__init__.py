from flask import Blueprint

message = Blueprint('message', __name__, template_folder='templates')

from . import views
