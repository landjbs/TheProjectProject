from flask import Flask, Response, abort, request
from base64 import b64decode

import os
from peewee import *


# 1 pixel GIF, base64-encoded.
BEACON = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


ANALYTIC_SCRIPT = '''
    """(function(){
    var d=document,i=new Image,e=encodeURIComponent;
    i.src='%s/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title);
    })()""".replace('\n', '')
'''



@app.route('/a.gif')
def analyze():
    ''' View analytics 1pixel gif '''
    pass


@app.route('/a.js')
def script():
    ''' View analytics javascript '''
    return Response(
        app.config['JAVASCRIPT'] % (app.config['DOMAIN']),
        mimetype='text/javascript')
