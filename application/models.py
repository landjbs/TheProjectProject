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
    name = Column(String(128), unique=False)
    # email
    email = Column(String(254), unique=True, nullable=False)
    # password
    password = Column(String(254), nullable=False)
    # subject
    subjects = relationship('Subject', backref='user', lazy=True,
                            cascade="all, delete-orphan")
    # github
    github = Column(String(254), unique=True, nullable=True)
    # about
    about = Column(String(500), nullable=False)
    # accepted
    accepted = Column(Boolean, nullable=False)
    ## projects ##
    # projects user created
    created_projects = relationship('Project', back_populates='creator')
    # # projects user applied to
    pending_projects = relationship('Project', secondary='user_to_project',
                                    back_populates='pending_users')
    # # # projects user is member in
    member_projects = relationship('Project', secondary='user_to_project',
                                    back_populates='members')

    def __init__(self, name, email, password, subjects, github, about):
        self.name = str(name)
        self.email = str(email)
        self.password = str(self.set_password(password))
        self.subjects = subjects if subjects else []
        self.github = str(github)
        self.about = str(about)
        self.accepted = False
        self.created_projects = []
        self.pending_projects = []
        self.member_projects = []

    def __repr__(self):
        return f'<User {self.name}>'

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
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship('User', back_populates='created_projects')
    # pending members
    pending_users = relationship('User', secondary='user_to_project',
                                 back_populates='pending_projects')
    # approved members
    members = relationship('User', secondary='user_to_project',
                           back_populates='member_projects')
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

    def __init__(self, name, summary, url, creator, open, requires_application,
                 application_question, estimated_time, complete):
        self.name = str(name)
        self.summary = str(summary)
        self.url = str(url)
        # members
        self.creator_id = int(creator.id)
        self.pending = []
        self.members = []
        # application
        self.open = bool(open)
        self.requires_application = bool(requires_application)
        self.application_question = str(application_question)
        # timing and completion
        cur_time = datetime.now()
        self.posted_on = cur_time
        self.completed_on = cur_time if complete else None
        self.estimated_time = estimated_time if not complete else None
        self.complete = bool(complete)

    def __repr__(self):
        return f'<Project {self.name}>'

# class Subject(db.Model):
#     __tablename__ = 'subject'
#     # id primary key
#     id = Column(Integer, primary_key=True)
#     # name
#     name = Column(String(128), unique=False, nullable=False,
#                      info={'label':'Name'})
#     # users
#     users = relationship('User')
#     # projects
#     projects = relationship('Project')
