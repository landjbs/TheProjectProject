from flask import Blueprint

badge = Blueprint('badge', __name__, template_folder='templates',
                  static_folder='static')

from . import views
