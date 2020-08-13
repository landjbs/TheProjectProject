from flask import Blueprint

link = Blueprint('link', __name__, template_folder='templates',
                  static_folder='static')

from . import views
