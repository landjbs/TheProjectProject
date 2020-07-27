import sys
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import (Table, Column, ForeignKey, Integer, String, Boolean,
                        DateTime, Float)
from sqlalchemy_utils import IntRangeType
from sqlalchemy import desc


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


user_to_project_2 = Table('user_to_project_2', db.Model.metadata,
                        Column('user_id', Integer, ForeignKey('user.id')),
                        Column('project_id', Integer, ForeignKey('project.id')))


user_to_task = Table('user_to_task', db.Model.metadata,
                    Column('user_id', Integer, ForeignKey('user.id')),
                    Column('task_id', Integer, ForeignKey('task.id')))


# stores users and notifcations they have recieved
user_to_notification = Table('user_to_notification', db.Model.metadata,
            Column('user_id', Integer, ForeignKey('user.id')),
            Column('notification_id', Integer, ForeignKey('notification.id')))


# stores invitations of users to join projects
project_invitation = Table('project_invitation', db.Model.metadata,
            Column('user_id', Integer, ForeignKey('user.id')),
            Column('project_id', Integer, ForeignKey('project.id')))


# stores users/projects rejected from each other
project_rejections = Table('project_rejections', db.Model.metadata,
                Column('user_id', Integer, ForeignKey('user.id')),
                Column('project_id', Integer, ForeignKey('project.id')))



class User_Subjects(db.Model):
    __tablename__ = 'user_subjects'
    # user
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='subjects')
    # subjects
    subject_id = Column(Integer, ForeignKey('subject.id'), primary_key=True)
    subject = relationship('Subject', back_populates='users')
    # count
    number = Column(Integer, nullable=False, default=1)


class Project_Application(db.Model):
    __tablename__ = 'project_application'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='pending')
    project_id = Column(Integer, ForeignKey('project.id'), primary_key=True)
    project = relationship('Project', back_populates='pending')
    text = Column('text', String(250), nullable=True)


## BASE CLASSES ##
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    # id primary key
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(128), unique=False)
    # code
    code = Column(String(128), nullable=False, unique=True)
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
    projects = relationship('Project', secondary='user_to_project_2',
                            back_populates='members')
    pending = relationship('Project_Application',
                            back_populates='user', lazy='dynamic')
    invitations = relationship('Project', secondary='project_invitation',
                               back_populates='invitations', lazy='dynamic')
    rejections = relationship('Project', secondary='project_rejections',
                            back_populates='rejections')
    # interactions
    starred = relationship('Project', secondary='user_to_project',
                           back_populates='stars')
    comments = relationship('Comment', back_populates='author')
    tasks_authored = relationship('Task', back_populates='author')
    tasks_worked = relationship('Task', secondary=user_to_task,
                         back_populates='workers')
    # notifications
    notifications = relationship('Notification', secondary=user_to_notification,
                                back_populates='users', lazy='dynamic',
                                order_by='Notification.timestamp')
    # subjects
    subjects = relationship('User_Subjects', back_populates='user',
                            lazy='dynamic', order_by='desc(User_Subjects.number)')

    def __init__(self, name, email, password, github, about):
        self.name = str(name)
        self.code = str(name).replace('/', '_').replace(' ', '_').lower()
        self.email = str(email)
        self.password = str(self.set_password(password))
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
            db.session.commit()

    def unstar_project(self, project):
        if self.has_starred(project):
            self.starred.remove(project)
            project.buzz -= 1
            db.session.commit()

    def has_starred(self, project):
        return (project in self.starred)

    def has_applied(self, project):
        return ((self.pending.filter_by(project=project).first()) is not None)


class Project(db.Model):
    __tablename__ = 'project'
    # id primary key
    id = Column(Integer, primary_key=True)
    ## base info ##
    # name
    name = Column(String(25), unique=False, nullable=False)
    # code for url
    code = Column(String(128), unique=True, nullable=False)
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
    members = relationship('User', secondary='user_to_project_2',
                           back_populates='projects', lazy='dynamic')
    pending = relationship('Project_Application',
                            back_populates='project', lazy='dynamic')
    invitations = relationship('User', secondary='project_invitation',
                               back_populates='invitations', lazy='dynamic')
    rejections = relationship('User', secondary='project_rejections',
                              back_populates='rejections')
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
        self.code = str(name).replace('/', '_').replace(' ', '_').lower()
        self.oneliner = str(oneliner)
        self.summary = str(summary)
        self.url = str(url) if url else None
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
    # code
    code = Column(String(128), unique=True, nullable=False)
    # users
    users = relationship('User_Subjects', back_populates='subject',
                         order_by='desc(User_Subjects.number)')
    # projects
    projects = relationship('Project', secondary='project_to_subject',
                            back_populates='subjects', lazy='dynamic')

    def __init__(self, name, color):
        self.name = str(name)
        self.color = str(color)
        self.code = str(name).replace('/', '_').replace(' ', '_').lower()
        self.users = []
        self.projects = []

    def __repr__(self):
        return f'<Subject {self.name}>'


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
    post_stamp = Column(DateTime, default=datetime.utcnow, index=True)
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
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Comment {self.author.name} on {self.project.name} at {self.timestamp}>'


class Notification(db.Model):
    __tablename__ = 'notification'
    # id
    id = Column(Integer, primary_key=True)
    # text
    text = Column(String(160), nullable=False)
    # user
    users = relationship('User', secondary=user_to_notification,
                         back_populates='notifications')
    # timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Badge(db.Model):
    __tablename__ = 'badge'
    # id
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(60), nullable=False, unique=True)
    # url for icon
    icon_url = Column(String(250), nullable=False, unique=True)
    # users
    users = relationship('User_Badge', back_populates='badge', lazy='dynamic')
