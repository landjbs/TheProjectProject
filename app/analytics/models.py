from flask import request
import json
from sqlalchemy import func
from datetime import datetime, timedelta
from urllib.parse import parse_qsl, urlparse

from app.database import db, CRUDMixin


class JSONField(db.Text):
    ''' Store json data from analytics as text '''
    def python_value(self, value):
        if value is not None:
            return json.loads(value)

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)


class PageView(CRUDMixin, db.Model):
    domain = db.Column(db.String())
    url = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    title = db.Column(db.Text(), default='')
    ip = db.Column(db.String(), default='')
    referrer = db.Column(db.Text(), default='')
    headers = db.Column(db.JSON())
    params = db.Column(db.JSON())

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

    ## pageview analytics ##
    @classmethod
    def views_over(cls, past_days):
        ''' Querys views over past_days '''
        if past_days:
            time_ago = (datetime.utcnow() - timedelta(past_days))
            return cls.query.filter(cls.timestamp >= time_ago)
        else:
            return cls.query.all()

    @classmethod
    def view_count(cls, past_days):
        return cls.views_over(past_days).count()

    @classmethod
    def user_count(cls, past_days=None):
        # TODO: rewrite in sql to be faster
        base = cls.views_over(past_days)
        # unique_users = cls.query
        unique_users = set(view.ip for view in base)
        return len(unique_users)
