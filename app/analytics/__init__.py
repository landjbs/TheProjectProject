from flask import Blueprint

analytics = Blueprint('analytics', __name__, template_folder='templates',
                  static_folder='static')

from . import views
