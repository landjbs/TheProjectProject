from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin
from app.extensions import bcrypt
# from app.models import (Project, Project_Application, Comment, Task, User_Badge,
                        # Notification, User_Subjects)
from app.models import (user_to_subject, user_to_project, user_to_project_2,
                        user_to_task, user_to_notification)


class User(CRUDMixin, UserMixin, db.Model):
    __tablename__ = 'user'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(128), unique=False)
    # code
    code = db.Column(db.String(128), nullable=False, unique=True)
    # email
    email = db.Column(db.String(254), unique=True, nullable=False)
    # password
    password = db.Column(db.String(254), nullable=False)
    # subject
    subjects = relationship('Subject', secondary='user_to_subject',
                            back_populates='users', lazy='dynamic')
    # github
    github = db.Column(db.String(254), unique=True, nullable=True)
    # about
    about = db.Column(db.String(500), nullable=False)
    ## permissions and other bools ##
    admin = db.Column(db.Boolean, nullable=False, default=False)
    emailed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    applied_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    accepted_on = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=False)
    last_active = db.Column(db.DateTime, nullable=True)
    ## projects ##
    owned = relationship('Project', back_populates='owner',
                         order_by='desc(Project.last_active)')
    projects = relationship('Project', secondary='user_to_project_2',
                            back_populates='members',
                            order_by='desc(Project.last_active)')
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

    def recently_active(self, second_window=302400):
        ''' second_window: number of seconds to count as recent.
            currently half a week.
            (week=604800), ()
        '''
        if self.active:
            return True
        if not self.last_active:
            return False
        diff = (db.DateTime.utcnow() - self.last_active).seconds
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
        self.accepted_on = db.DateTime.utcnow()
        db.session.commit()
        return True

    def reject(self):
        self.accepted = False
        self.accepted_on = None
        db.session.commit()
        return True

    # password
    def set_password(self, password):
        hash_ = bcrypt.generate_password_hash(password, 10).decode('utf-8')
        self.password = hash_

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

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
