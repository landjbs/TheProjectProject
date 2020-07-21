import sys
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import (Table, Column, ForeignKey, Integer, String, Boolean,
                        DateTime)
from sqlalchemy_utils import IntRangeType

sys.path.append('.')
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
        Column('project_id', Integer, ForeignKey('project.id')))


role_to_member_role = Table('role_to_member_role', db.Model.metadata,
                Column('role_id', Integer, ForeignKey('role.id')),
                Column('member_role_id', Integer, ForeignKey('member_role.id')))


user_to_task = Table('user_to_task', db.Model.metadata,
                Column('user_id', Integer, ForeignKey('user.id')),
                Column('task_id', Integer, ForeignKey('task.id')))


class Member_Role(db.Model):
    __tablename__ = 'member_role'
    # primary key
    id = Column(Integer, primary_key=True)
    # members
    user_id = Column('user_id', ForeignKey('user.id'), nullable=True)
    user = relationship('User', back_populates='projects')
    # projects
    project_id = Column('project_id', ForeignKey('project.id'), nullable=False)
    project = relationship('Project', back_populates='members')
    # roles
    roles = relationship('Role', secondary=role_to_member_role)
    # commits
    commits = Column(Integer, nullable=False, default=0)
    # tasks completed
    # tasks = relationship('Task', secondary=task_to_member_role,
                         # back_populates='members')


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
                            back_populates='users', lazy='dynamic')
    # github
    github = Column(String(254), unique=True, nullable=True)
    # about
    about = Column(String(500), nullable=False)
    # accepted
    accepted = Column(Boolean, nullable=False)
    ## projects ##
    owned = relationship('Project', back_populates='owner')
    projects = relationship('Member_Role', back_populates='user', lazy='dynamic')
    pending_projects = relationship('Project', secondary=user_to_project,
                                    back_populates='pending_members')
    # interactions
    starred = relationship('Project', secondary='user_to_project',
                           back_populates='stars')
    comments = relationship('Comment', back_populates='author')
    tasks_authored = relationship('Task', back_populates='author')
    tasks_worked = relationship('Task', secondary=user_to_task,
                         back_populates='workers')

    def __init__(self, name, email, password, subjects, github, about):
        self.name = str(name)
        self.email = str(email)
        self.password = str(self.set_password(password))
        self.subjects = subjects if subjects else []
        self.github = str(github) if github!='' else None
        self.about = str(about)
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

    def star_project(self, project):
        if not self.has_starred(project):
            self.starred.append(project)
            project.buzz += 1

    def unstar_project(self, project):
        if self.has_starred(project):
            self.starred.remove(project)
            project.buzz -= 1

    def has_starred(self, project):
        return (project in self.starred)


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
                            back_populates='projects', lazy='dynamic')
    ## people ##
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', back_populates='owned')
    members = relationship('Member_Role', back_populates='project', lazy='dynamic')
    pending_members = relationship('User', secondary=user_to_project, back_populates='pending_projects')
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
    ## popularity ##
    # stars
    stars = relationship('User', secondary='user_to_project',
                         back_populates='starred', lazy='dynamic')
    # buzz
    buzz = Column(Integer, nullable=False)
    # comments
    comments = relationship('Comment', back_populates='project')
    # tasks
    tasks = relationship('Task', back_populates='project', lazy='dynamic')

    def __init__(self, name, oneliner, summary, url, open, subjects,
                requires_application, application_question, estimated_time,
                team_size, complete, owner):
        self.name = str(name)
        self.oneliner = str(oneliner)
        self.summary = str(summary)
        self.url = str(url)
        self.subjects = subjects
        # members
        self.owner = owner
        self.team_size = team_size
        # application
        self.open = bool(open)
        self.requires_application = bool(requires_application)
        self.application_question = str(application_question) if requires_application else None
        # timing and completion
        cur_time = datetime.now()
        self.posted_on = cur_time
        self.completed_on = cur_time if complete else None
        self.estimated_time = estimated_time if not complete else None
        self.complete = bool(complete)
        self.buzz = 0

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
                        back_populates='subjects', lazy='dynamic')
    # projects
    projects = relationship('Project', secondary='project_to_subject',
                            back_populates='subjects', lazy='dynamic')

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
    # projects
    projects = relationship('Member_Role', secondary=role_to_member_role,
                            back_populates='roles', lazy='dynamic')

    def __init__(self, name, color):
        self.name = str(name)
        self.color = str(name)

    def __repr__(self):
        return f'<Role {self.name}>'


class Task(db.Model):
    __tablename__ = 'task'
    # id
    id = Column(Integer, primary_key=True)
    # text
    text = Column(String(160), nullable=True)
    # author
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', back_populates='tasks_authored')
    # project
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='tasks')
    # workers
    workers = relationship('User', secondary=user_to_task,
                           back_populates='tasks_worked')
    # timing
    post_stamp = Column(DateTime, default=datetime.utcnow(), index=True)
    complete_stamp = Column(DateTime, nullable=True)
    complete = Column(Boolean, default=False)

    def mark_complete(self, worker):
        if not self.complete:
            self.add_worker(worker)
            self.complete = True
            self.complete_stamp = datetime.utcnow()

    def mark_incomplete(self):
        if self.complete:
            self.complete = False
            self.complete_stamp = None

    def add_worker(self, worker):
        self.workers.append(worker)


class Comment(db.Model):
    __tablename__ = 'comment'
    # id
    id = Column(Integer, primary_key=True)
    # text
    text = Column(String(160), nullable=False)
    # author
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', back_populates='comments')
    # project
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='comments')
    # time
    timestamp = Column(DateTime, default=datetime.utcnow(), index=True)

    def __repr__(self):
        return f'<Comment {self.author.name} on {self.project.name} at {self.timestamp}>'
