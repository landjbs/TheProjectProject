from flask import Blueprint

project = Blueprint('project', __name__, template_folder='templates', static_url_path='/',
                    static_folder='static')

from . import views
