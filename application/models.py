import sys
import numpy as np
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import (Table, Column, ForeignKey, Integer, String, Boolean,
                        DateTime, Float)
from sqlalchemy_utils import IntRangeType
from sqlalchemy import desc


sys.path.append('.')
from application import db


def generate_code(name, table):
    code = str(name).replace('/', '_').replace(' ', '_').lower()
    temp_code = f'{code}_{str(np.random.randint(0, 1000))}'
    while table.query.filter_by(code=temp_code).first() is not None:
        temp_code = f'{code}_{str(np.random.randint(0, 1000))}'
    return temp_code


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

    def __repr__(self):
        return f'<USER_SUBJECT u={self.user.name} s={self.subject.name} n={self.number}>'


class User_Badge(db.Model):
    __tablename__ = 'user_badge'
    # user
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='badges')
    # badges
    badge_id = Column(Integer, ForeignKey('badge.id'), primary_key=True)
    badge = relationship('Badge', back_populates='users')
    # progress
    progress = Column(Float, nullable=False, default=float(0))
    earned = Column(Boolean, nullable=False, default=False)
    earn_stamp = Column(DateTime, nullable=True)

    def __repr__(self):
        if not self.earned:
            return f'<USER_BADGE u={self.user.name} b={self.badge.name} p={self.progress}>'
        else:
            return f'<USER_BADGE u={self.user.name} b={self.badge.name} e={self.earn_stamp}>'


class Project_Application(db.Model):
    __tablename__ = 'project_application'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='pending')
    project_id = Column(Integer, ForeignKey('project.id'), primary_key=True)
    project = relationship('Project', back_populates='pending')
    text = Column('text', String(250), nullable=True)

    def __repr__(self):
        return f'<Application of {self.user.name} to {self.project.name}; Text={self.text}>'


## BASE CLASSES ##
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        super(Anonymous, self).__init__()

    def is_admin(self):
        return False

    def has_starred(self, project):
        return False

    def has_applied(self, project):
        return False


class Admin_User(db.Model, UserMixin):
    __tablename__ = 'admin_user'
    # id
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(128), unique=False)
    # email
    email = Column(String(254), unique=True, nullable=False)
    # password
    password = Column(String(254), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = self.set_password(password)

    def __repr__(self):
        return f'<Admin_User {self.name}>'

    def set_password(self, password):
        return str(generate_password_hash(password))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return True


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
    ## permissions and other bools ##
    admin = Column(Boolean, nullable=False, default=False)
    emailed = Column(Boolean, nullable=False, default=False)
    confirmed = Column(Boolean, nullable=False, default=False)
    accepted = Column(Boolean, nullable=False, default=False)
    applied_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    accepted_on = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=False, default=False)
    last_active = Column(DateTime, nullable=True)
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
    badges = relationship('User_Badge', back_populates='user', lazy='dynamic')
    # notifications
    notifications = relationship('Notification', secondary=user_to_notification,
                                back_populates='users', lazy='dynamic',
                                order_by='Notification.timestamp')
    # subjects
    subjects = relationship('User_Subjects', back_populates='user',
                            lazy='dynamic', order_by='desc(User_Subjects.number)')
    ## reporting ##
    # reports posted by user
    # reports_posted = relationship('User_Report', back_populates='reporter')
    # reports targeting user
    reports = relationship('User_Report',
                           back_populates='reported',
                           primaryjoin='User.id==User_Report.reported_id',
                           lazy='dynamic')


    def __init__(self, name, email, password, github, about, admin=False):
        self.name = str(name)
        self.code = generate_code(name, User)
        self.email = str(email)
        self.password = self.set_password(password)
        self.github = str(github) if github!='' else None
        self.about = str(about)
        self.admin = admin
        self.accepted = True if admin else False
        self.emailed = True if admin else False
        self.confirmed = True if admin else False

    def __repr__(self):
        return f'<User {self.name}>'

    # auth/login
    def get_id(self):
        return str(self.id)

    def is_active(self):
        return self.active

    def recently_active(self, second_window=60):
        if self.active:
            return True
        if not self.last_active:
            return False
        diff = (datetime.utcnow() - self.last_active).seconds
        if diff>second_window:
            return False
        return True


    def is_authenticated(self):
        return self.accepted

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.admin

    def accept(self):
        # if not self.confirmed:
            # raise RuntimeError(f'{self} email has not been confirmed.')
        # elif self.accepted:
            # raise RuntimeError(f'{self} has already been accepted.')
        self.accepted = True
        self.accepted_on = datetime.utcnow()
        db.session.commit()
        return True

    def reject(self):
        self.accepted = False
        self.accepted_on = None
        db.session.commit()
        return True

    # password
    def set_password(self, password):
        return str(generate_password_hash(password))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # starring
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

    # applications
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
        self.code = generate_code(name, User)
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
    author_id = Column(Integer, ForeignKey('user.id'), nullable=True)
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
        return f'<Comment {self.author.name} on {self.project.name} at {self.timestamp}; TEXT={self.text}>'


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

    def __repr__(self):
        return f'<Notification to {self.users} at {self.timestamp}; TEXT={self.text}>'


class Badge(db.Model):
    __tablename__ = 'badge'
    # id
    id = Column(Integer, primary_key=True)
    # name
    name = Column(String(60), nullable=False, unique=True)
    # url for icon
    icon_url = Column(String(250), nullable=False, unique=True)
    # color
    color = Column(String(6), unique=True, nullable=False)
    # users
    users = relationship('User_Badge', back_populates='badge', lazy='dynamic')

    def __repr__(self):
        return f'<Badge {self.name}>'


class User_Report(db.Model):
    __tablename__ = 'user_report'
    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey(User.id))
    reported_id = Column(Integer, ForeignKey(User.id))
    reporter = relationship('User', foreign_keys='User_Report.reporter_id')
    reported = relationship('User', foreign_keys='User_Report.reported_id')
    ## description ##
    # report description
    text = Column('text', String(250), nullable=True)
    # report time
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    ## administrative ##
    # has report been addressed
    resolved = Column(Boolean, nullable=False, default=False)
    # action: what action was taken {0:pass, 1:warning, 2:tempban, 3:permaban}
    action = Column(Integer, nullable=True)
    # resolve_stamp: when action was taken
    resolve_stamp = Column(DateTime, nullable=True)

    def __repr__(self):
        base = (f'<Report of {self.reported} by {self.reporter} at {self.timestamp}; '
                f'TEXT={self.text}')
        if not self.resolved:
            return (base + f'resolved with {self.action} at {self.resolve_stamp}>')
        else:
            return base + '>'

    def resolve(action):
        ''' action = {0:pass, 1:warning, 2:tempban, 3:permaban} '''
        self.resolved = True
        self.action = int(action)
        self.resolve_stamp = datetime.utcnow()
