from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from application import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(128), index=True, unique=False,
                     info={'label':'Name'})
    # email
    email = db.Column(db.String(254), unique=False, nullable=False,
                      info={'label':'Havard Email '})
    # password
    password = db.Column(db.String(254), nullable=False,
                         info={'label':'Password'})
    # github
    github = db.Column(db.String(254), nullable=True,
                         info={'label':'Github'})
    # about
    about = db.Column(db.String(500), nullable=False,
                      info={'label':'About'})
    # accepted
    accepted = db.Column(db.Boolean, nullable=False)
    # subject
    subjects = relationship('Subject', backref='user', lazy=True,
                            cascade="all, delete-orphan")
    # projects
    projects = relationship('Project', backref='user', lazy=True,
                            cascade="all, delete-orphan")

    def __init__(self, name, email, password, github, about):
        self.name = name
        self.email = email
        self.password = self.set_password(password)
        self.github = github
        self.about = about
        self.accepted = False # status set to "applied"

    def __repr__(self):
        return '<User %r>' % self.name

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Project(db.Model):
    __tablename__ = 'project'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    ## base info ##
    # name
    name = db.Column(db.String(128), unique=False, nullable=False,
                     info={'label':'Name'})
    # summary
    summary = db.Column(db.String(500), unique=False, nullable=False,
                        info={'label':'Summary'})
    # url
    url = db.Column(db.String(128), unique=False, nullable=True,
                    info={'label':'URL'})
    # specialty
    specialty = db.Integer()
    ## people ##
    # creator
    creator = db.Column(db.Integer, ForeignKey('user.id'),
                        nullable=False)
    # open (allows others to join)
    open = db.Column(db.Boolean, nullable=False)
    # pending members
    pending = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    # approved members
    members = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    ## timing ##
    # posted_on
    posted_on = db.Column(db.DateTime, nullable=False,
                          info={'label':'Posted On'})
    # complete_on
    completed_on = db.Column(db.DateTime, nullable=True,
                             info={'label':'Completed On'})
    # estimated time
    estimated_time = db.Column(db.Float, nullable=True,
                               info={'label':'Estimated time'})
    # complete
    complete = db.Column(db.Boolean, nullable=False, info={'label':'Complete'})

    def __init__(self, creator, name, summary, url):



class Subject(db.Model):
    __tablename__ = 'subject'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(128), unique=False, nullable=False,
                     info={'label':'Name'})
    # users
    users = relationship('User')
    # projects
    projects = relationship('Project')

    # def __init__(self, )
