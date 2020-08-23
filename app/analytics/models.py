from flask import request
import json
from datetime import datetime
from urlparse import parse_qsl, urlparse

from app.database import db, CRUDMixin


class JSONField(db.TextField):
    ''' Store json data from analytics as text '''
    def python_value(self, value):
        if value is not None:
            return json.loads(value)

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)


class PageView(CRUDMixin, db.Model):
    domain = db.CharField()
    url = db.TextField()
    timestamp = db.DateTimeField(default=datetime.utcnow, index=True)
    title = db.TextField(default='')
    ip = db.CharField(default='')
    referrer = TextField(default='')
    headers = JSONField()
    params = JSONField()

    class Meta:
        database = db

    @classmethod
    def create_from_request(cls):
        parsed = urlparse(request.args['url'])
        params = dict(parse_qsl(parsed.query))
        return PageView.create(
            domain=parsed.netloc,
            url=parsed.path,
            title=request.args.get('t') or '',
            ip=request.headers.get('X-Forwarded-For', request.remote_addr),
            referrer=request.args.get('ref') or '',
            headers=dict(request.headers),
            params=params
        )
