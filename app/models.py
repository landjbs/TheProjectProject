from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import (Table, ForeignKey, Integer, String, Boolean,
                        DateTime, Float)
from sqlalchemy_utils import IntRangeType
from sqlalchemy import desc


from app.database import db, generate_code


## ASSOCIATION TABLES ##
user_to_subject = Table('user_to_subject', db.Model.metadata,
                      db.Column('user_id', Integer, ForeignKey('user.id')),
                      db.Column('subject_id', Integer, ForeignKey('subject.id')))


project_to_subject = Table('project_to_subject', db.Model.metadata,
                        db.Column('project_id', Integer, ForeignKey('project.id')),
                        db.Column('subject_id', Integer, ForeignKey('subject.id')))


user_to_project = Table('user_to_project', db.Model.metadata,
                        db.Column('user_id', Integer, ForeignKey('user.id')),
                        db.Column('project_id', Integer, ForeignKey('project.id')))


user_to_project_2 = Table('user_to_project_2', db.Model.metadata,
                        db.Column('user_id', Integer, ForeignKey('user.id')),
                        db.Column('project_id', Integer, ForeignKey('project.id')))


user_to_task = Table('user_to_task', db.Model.metadata,
                    db.Column('user_id', Integer, ForeignKey('user.id')),
                    db.Column('task_id', Integer, ForeignKey('task.id')))


# stores users and notifcations they have recieved
user_to_notification = Table('user_to_notification', db.Model.metadata,
            db.Column('user_id', Integer, ForeignKey('user.id')),
            db.Column('notification_id', Integer, ForeignKey('notification.id')))


# stores invitations of users to join projects
project_invitation = Table('project_invitation', db.Model.metadata,
            db.Column('user_id', Integer, ForeignKey('user.id')),
            db.Column('project_id', Integer, ForeignKey('project.id')))


# stores users/projects rejected from each other
project_rejections = Table('project_rejections', db.Model.metadata,
                db.Column('user_id', Integer, ForeignKey('user.id')),
                db.Column('project_id', Integer, ForeignKey('project.id')))



class User_Subjects(db.Model):
    __tablename__ = 'user_subjects'
    # user
    user_id = db.Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='subjects')
    # subjects
    subject_id = db.Column(Integer, ForeignKey('subject.id'), primary_key=True)
    subject = relationship('Subject', back_populates='users')
    # count
    number = db.Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<USER_SUBJECT u={self.user.name} s={self.subject.name} n={self.number}>'


class User_Badge(db.Model):
    __tablename__ = 'user_badge'
    # user
    user_id = db.Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='badges')
    # badges
    badge_id = db.Column(Integer, ForeignKey('badge.id'), primary_key=True)
    badge = relationship('Badge', back_populates='users')
    # progress
    progress = db.Column(Float, nullable=False, default=float(0))
    earned = db.Column(Boolean, nullable=False, default=False)
    earn_stamp = db.Column(DateTime, nullable=True)

    def __repr__(self):
        if not self.earned:
            return f'<USER_BADGE u={self.user.name} b={self.badge.name} p={self.progress}>'
        else:
            return f'<USER_BADGE u={self.user.name} b={self.badge.name} e={self.earn_stamp}>'


class Project_Application(db.Model):
    __tablename__ = 'project_application'
    user_id = db.Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='pending')
    project_id = db.Column(Integer, ForeignKey('project.id'), primary_key=True)
    project = relationship('Project', back_populates='pending')
    text = db.Column('text', String(250), nullable=True)

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



class Task(db.Model):
    __tablename__ = 'task'
    # id
    id = db.Column(Integer, primary_key=True)
    # text
    text = db.Column(String(160), nullable=True)
    # author
    author_id = db.Column(Integer, ForeignKey('user.id'), nullable=True)
    author = relationship('User', back_populates='tasks_authored')
    # project
    project_id = db.Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='tasks')
    # workers
    workers = relationship('User', secondary=user_to_task,
                           back_populates='tasks_worked')
    # timing
    post_stamp = db.Column(DateTime, default=datetime.utcnow, index=True)
    complete_stamp = db.Column(DateTime, nullable=True)
    complete = db.Column(Boolean, default=False)

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
    id = db.Column(Integer, primary_key=True)
    # text
    text = db.Column(String(160), nullable=False)
    # author
    author_id = db.Column(Integer, ForeignKey('user.id'))
    author = relationship('User', back_populates='comments')
    # project
    project_id = db.Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='comments')
    # time
    timestamp = db.Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Comment {self.author.name} on {self.project.name} at {self.timestamp}; TEXT={self.text}>'
        

class Badge(db.Model):
    __tablename__ = 'badge'
    # id
    id = db.Column(Integer, primary_key=True)
    # name
    name = db.Column(String(60), nullable=False, unique=True)
    # url for icon
    icon_url = db.Column(String(250), nullable=False, unique=True)
    # color
    color = db.Column(String(6), unique=True, nullable=False)
    # users
    users = relationship('User_Badge', back_populates='badge', lazy='dynamic')

    def __repr__(self):
        return f'<Badge {self.name}>'
