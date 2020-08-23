from flask import render_template, send_from_directory, current_app, request

from ..base import base


@base.route('/', methods=['GET'])
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
