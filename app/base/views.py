from flask import render_template, redirect, url_for
from flask_login import current_user

from ..base import base


@base.route('/', methods=['GET'])
def domain():
    if current_user.is_authenticated and current_user.is_active:
        return redirect(url_for('hub.home'))
    return redirect(url_for('base.index'))


@base.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@base.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@base.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@base.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')
