from flask import current_app, Response, abort, request
from peewee import *

from .models import PageView, db
from ..analytics import analytics



@app.route('/a.gif')
def analyze():
    ''' View analytics 1pixel gif '''
    print('analysis')
    if not request.args.get('url'):
        abort(404)

    with db.transaction():
        PageView.create_from_request()

    response = Response(current_app.config['BEACON'], mimetype='image/gif')
    response.headers['Cache-Control'] = 'private, no-cache'
    return response


@app.route('/a.js')
def script():
    ''' View analytics javascript '''
    print('scripting')
    return Response(
        app.config['ANALYTIC_SCRIPT'] % (app.config['DOMAIN']),
        mimetype='text/javascript')
