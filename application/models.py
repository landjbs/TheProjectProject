from application import db
from flask_login import UserMixin


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=False, info={'label':'Password'})
    # email = db.Column(db.String(254), unique=False, nullable=False,
                      # info={'label':'Email Address'})
    # password
    password = db.Column(db.String(254), nullable=False, info={'label':'Password'})

    def __init__(self, name, password): # name, password
        self.name = name
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name


class User(db.Model, UserMixin):
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(128), index=True, unique=False, info={'label':'Name'})
    # email
    email = db.Column(db.String(254), unique=False, nullable=False,
                      info={'label':'Email Address'})
    # password
    password = db.Column(db.String(254), nullable=False, info={'label':'Password'})
