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


# badge to perks
badge_to_perk = Table('badge_to_perk', db.Model.metadata,
                    db.Column('badge_id', Integer, ForeignKey('badge.id')),
                    db.Column('perk_id', Integer, ForeignKey('Badge_Perk.id')))


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
