from flask import current_app, Response, abort, request
from peewee import *

from .models import PageView, db
from ..analytics import analytics


@analytics.route('/a.gif')
def analyze():
    ''' View analytics 1pixel gif '''
    if not request.args.get('url'):
        abort(404)

    PageView.create_from_request()

    response = Response(current_app.config['BEACON'], mimetype='image/gif')
    response.headers['Cache-Control'] = 'private, no-cache'
    return response


@analytics.route('/a.js')
def script():
    ''' View analytics javascript '''
    return Response(
        current_app.config['ANALYTIC_SCRIPT'] % (current_app.config['DOMAIN']),
        mimetype='text/javascript')
