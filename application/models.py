from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean

from application import db


## ASSOCIATION TABLES ##
user_to_subject = Table('user_to_subject', db.Model.metadata,
                      Column('user_id', Integer, ForeignKey('user.id')),
                      Column('subject_id', Integer, ForeignKey('subject.id')))

project_to_subject = Table('project_to_subject', db.Model.metadata,
                        Column('user_id', Integer, ForeignKey('user.id')),
                        Column('project_id', Integer, ForeignKey('project.id')))

user_to_project = Table('user_to_project', db.Model.metadata,
                    Column('user_id', Integer, ForeignKey('user.id')),
                    Column('project_id', Integer, ForeignKey('project.id')))


## BASE CLASSES ##
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    # id primary key
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(128), index=True, unique=False,
                     info={'label':'Name'})
    # email
    email = Column(String(254), unique=False, nullable=False,
                      info={'label':'Havard Email '})
    # password
    password = Column(String(254), nullable=False,
                         info={'label':'Password'})
    # github
    github = Column(String(254), nullable=True,
                         info={'label':'Github'})
    # about
    about = Column(String(500), nullable=False,
                      info={'label':'About'})
    # accepted
    accepted = Column(Boolean, nullable=False)
    # subject
    subjects = relationship('Subject', backref='user', lazy=True,
                            cascade="all, delete-orphan")
    ## projects ##
    # projects user created
    created_projects = relationship('Project', backref='user', lazy=True,
                                    cascade="all, delete-orphan")
    # # projects user applied to
    pending_projects = relationship('Project', secondary=user_to_project,
                                    back_populates='parents')
    # # projects user is member in
    # member_projects = relationship('Project', backref='user', lazy=True,
    #                                cascade="all, delete-orphan"))


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
    id = Column(Integer, primary_key=True)
    ## base info ##
    # name
    name = Column(String(128), unique=True, nullable=False,
                     info={'label':'Name'})
    # summary
    summary = Column(String(500), nullable=False,
                        info={'label':'Summary'})
    # url
    url = Column(String(128), unique=True, nullable=True,
                    info={'label':'URL'})
    # subject
    # subjects = Column(db.)
    ## people ##
    # creator
    creator = Column(Integer, ForeignKey('user.id'))
    # pending members
    pending = relationship('User', secondary=user_to_project,
                           back_populates='children')
    # approved members
    members = relationship('User', secondary=user_to_project,
                           back_populates='children')
    ## join process ##
    # open (allows others to join)
    open = Column(Boolean, nullable=False)
    # requires application
    requires_application = Column(Boolean, nullable=False)
    # applicaiton question
    application_question = Column(String(250), nullable=True)
    ## timing ##
    # posted_on
    posted_on = Column(db.DateTime, nullable=False,
                          info={'label':'Posted On'})
    # complete_on
    completed_on = Column(db.DateTime, nullable=True,
                             info={'label':'Completed On'})
    # estimated time
    estimated_time = Column(db.Float, nullable=True,
                               info={'label':'Estimated time'})
    # complete
    complete = Column(Boolean, nullable=False, info={'label':'Complete'})

    # def __init__(self, creator, name, summary, url):


class Subject(db.Model):
    __tablename__ = 'subject'
    # id primary key
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(128), unique=False, nullable=False,
                     info={'label':'Name'})
    # users
    users = relationship('User')
    # projects
    projects = relationship('Project')

    # def __init__(self, )
