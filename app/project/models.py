from db.DateTime import db.DateTime
from sqlalchemy import desc
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin, generate_code


class Project(CRUDMixin, db.Model):
    __tablename__ = 'project'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    ## base info ##
    # name
    name = db.Column(db.String(25), unique=False, nullable=False)
    # code for url
    code = db.Column(db.String(128), unique=True, nullable=False)
    # oneliner
    oneliner = db.Column(db.String(40))
    # summary
    summary = db.Column(db.String(400), nullable=False)
    # url
    url = db.Column(db.String(128), nullable=True)
    # subject
    subjects = relationship('Subject', secondary='project_to_subject',
                            back_populates='projects', lazy='dynamic')
    ## people ##
    owner_id = db.Column(db.Integer, ForeignKey('user.id'))
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
    open = db.Column(db.Boolean, nullable=False)
    # requires application
    requires_application = db.Column(db.Boolean, nullable=False)
    # applicaiton question
    application_question = db.Column(db.String(128), nullable=True)
    # max team size
    team_size = db.Column(db.Integer, nullable=False)
    ## timing ##
    # posted_on
    posted_on = db.Column(db.DateTime, nullable=False)
    # complete_on
    completed_on = db.Column(db.DateTime, nullable=True)
    # last activity
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # estimated time
    estimated_time = db.Column(db.Integer, nullable=True)
    # complete
    complete = db.Column(db.Boolean, nullable=False)
    ## popularity ##
    # stars
    stars = relationship('User', secondary='user_to_project',
                         back_populates='starred', lazy='dynamic')
    # buzz
    buzz = db.Column(db.Integer, nullable=False)
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
        cur_time = datetime.utcnow()
        self.posted_on = cur_time
        self.completed_on = cur_time if complete else None
        self.estimated_time = estimated_time if not complete else None
        self.complete = bool(complete)
        self.buzz = 0

    def __repr__(self):
        return f'<Project {self.name}>'

    def recently_active(self, second_window=302400):
        ''' second_window: number of seconds to count as recent.
            currently half a week.
            (week=604800), ()
        '''
        if not self.last_active:
            return False
        diff = (datetime.utcnow() - self.last_active).seconds
        if diff>second_window:
            return False
        return True

    def task_number(self):
        # TODO: make efficient
        n = 0
        for task in self.tasks:
            n += 1
        return n

    def update_last_active(self):
        self.last_active = datetime.utcnow()
