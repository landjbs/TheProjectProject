from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin, generate_code


class Subject(CRUDMixin, db.Model): # SearchableMixin
    __tablename__ = 'subject'
    # __searchable__ = ['name']
    # name
    name = db.Column(db.String(128), unique=True, nullable=False)
    # color
    color = db.Column(db.String(7), unique=True, nullable=False)
    # code
    code = db.Column(db.String(128), unique=True, nullable=False)
    # users
    users = relationship('User_Subjects', back_populates='subject',
                         order_by='desc(User_Subjects.number)')
    # projects
    projects = relationship('Project', secondary='project_to_subject',
                            back_populates='subjects', lazy='dynamic')

    def __init__(self, name, color):
        self.name = str(name)
        self.color = str(color)
        self.code = generate_code(name, Subject)
        self.users = []
        self.projects = []

    def __repr__(self):
        return f'<Subject {self.name}>'


class User_Subjects(db.Model):
    __tablename__ = 'user_subjects'
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='subjects')
    # subjects
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)
    subject = relationship('Subject', back_populates='users')
    # count
    number = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<USER_SUBJECT u={self.user.name} s={self.subject.name} n={self.number}>'
