from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import (Table, Column, ForeignKey, Integer, String, Boolean,
                        DateTime)
from sqlalchemy_utils import IntRangeType

from application import db


## ASSOCIATION TABLES ##
user_to_subject = Table('user_to_subject', db.Model.metadata,
                      Column('user_id', Integer, ForeignKey('user.id')),
                      Column('subject_id', Integer, ForeignKey('subject.id')))

project_to_subject = Table('project_to_subject', db.Model.metadata,
                        Column('project_id', Integer, ForeignKey('project.id')),
                        Column('subject_id', Integer, ForeignKey('subject.id')))

user_to_project = Table('user_to_project', db.Model.metadata,
        Column('user_id', Integer, ForeignKey('user.id')),
        Column('project_id', Integer, ForeignKey('project.id')),
        Column('role_id', Integer))


class Member_Role(db.Model):
    __tablename__ = 'role'
    # primary key
    id = Column(Integer, primary_key=True)
    # members
    user_id = Column('user_id', ForeignKey('user.id'), nullable=True)
    user = relationship('User', back_populates='projects')
    # projects
    project_id = Column('project_id', ForeignKey('project.id'))
    project = relationship('Project', back_populates='members')
    # roles
    # role_id = Column('role_id', Integer)
    role_id = Column('role_id', ForeignKey('role.id'))
    role = relationship('Role', back_populates='projects')


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
    subjects = relationship('Subject', secondary='user_to_subject',
                            back_populates='users')
    # github
    github = Column(String(254), unique=True, nullable=True)
    # about
    about = Column(String(500), nullable=False)
    # accepted
    accepted = Column(Boolean, nullable=False)
    ## projects ##
    # projects user created
    projects = relationship('Member_Role', back_populates='user')
    # created_projects = relationship('Project', back_populates='creator')
    # # # projects user applied to
    # pending_projects = relationship('Project', secondary='user_to_project',
    #                                 back_populates='pending_users')
    # # # # projects user is member in
    # member_projects = relationship('Project', secondary='user_to_project',
    #                                 back_populates='members')

    def __init__(self, name, email, password, subjects, github, about):
        self.name = str(name)
        self.email = str(email)
        self.password = str(self.set_password(password))
        self.subjects = subjects if subjects else []
        self.github = str(github) if github!='' else None
        self.about = str(about)
        # self.projects = []
        self.accepted = False

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
    name = Column(String(25), unique=True, nullable=False)
    # oneliner
    oneliner = Column(String(40))
    # summary
    summary = Column(String(400), nullable=False)
    # url
    url = Column(String(128), nullable=True)
    # subject
    subjects = relationship('Subject', secondary='project_to_subject',
                            back_populates='projects')
    ## people ##
    # creator
    members = relationship('Member_Role', back_populates='project')
    # members = relationship('User', secondary='user_to_project',
    #                         back_populates='pending_projects')
    # creator_id = Column(Integer, ForeignKey('user.id'))
    # creator = relationship('User', back_populates='created_projects')
    # pending members
    # pending_users = relationship('User', secondary='user_to_project',
    #                              back_populates='pending_projects')
    # # approved members
    # members = relationship('User', secondary='user_to_project',
    #                        back_populates='member_projects')
    ## join process ##
    # open (allows others to join)
    open = Column(Boolean, nullable=False)
    # requires application
    requires_application = Column(Boolean, nullable=False)
    # applicaiton question
    application_question = Column(String(128), nullable=True)
    # max team size
    team_size = Column(Integer, nullable=False)
    ## timing ##
    # posted_on
    posted_on = Column(DateTime, nullable=False)
    # complete_on
    completed_on = Column(DateTime, nullable=True)
    # estimated time
    estimated_time = Column(Integer, nullable=True)
    # complete
    complete = Column(Boolean, nullable=False)
    ## buzz ##
    stars = Column(Integer, nullable=False)

    def __init__(self, name, oneliner, summary, url, open,
                requires_application, application_question, estimated_time,
                team_size, complete):
        self.name = str(name)
        self.oneliner = str(oneliner)
        self.summary = str(summary)
        self.url = str(url)
        # members
        self.members = []
        # self.creator_id = int(creator.id)
        # self.pending = []
        # self.members = []
        self.team_size = team_size
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
        # buzz
        self.stars = 0

    def __repr__(self):
        return f'<Project {self.name}>'


class Subject(db.Model):
    __tablename__ = 'subject'
    # id primary key
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(128), unique=True, nullable=False)
    # color
    color = Column(String(6), unique=True, nullable=False)
    # users
    users = relationship('User', secondary='user_to_subject',
                        back_populates='subjects')
    # projects
    projects = relationship('Project', secondary='project_to_subject',
                            back_populates='subjects')

    def __init__(self, name, color):
        self.name = str(name)
        self.users = []
        self.projects = []
        self.color = str(color)

    def __repr__(self):
        return f'<Subject {self.name}>'


class Role(db.Model):
    __tablename__ = 'role'
    # id
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(40), unique=True, nullable=False)
    # color
    color = Column(String(6), unique=True, nullable=False)

    def __init__(self, name, color):
        self.name = str(name)
        self.color = str(name)

    def __repr__(self):
        return f'<Role {self.name}>'
