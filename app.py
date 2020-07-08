import gc
import sys
import json
from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import current_user, login_user, logout_user, login_required
from flask_user import roles_required
from werkzeug.urls import url_parse

from forms import Application


app = Flask(__name__, static_url_path='', static_folder='static')
# configure
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.debug = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


@app.route('/index')
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()


# def create_app():
#     app = Flask(__name__, static_url_path='', static_folder='static')
#     app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#     app.debug = True
#     app.config['SQLALCHEMY_DATABASE_URI'] = URI
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#     manager.loginManager.init_app(app)
#     # manager.mail.init_app(app)
#     app.app_context().push()
#     return app
