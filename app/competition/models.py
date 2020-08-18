from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin, generate_code



class Competition(CRUDMixin, db.Model):
    __tablename__ = 'competition'
    # name
    name = db.Column(db.String(128), nullable=False)
    # code
    code = db.Column(db.String(128), nullable=False, unique=True)
    # sponsor
    sponsor = db.Column(db.String(400), nullable=False, default='TheProjectProject')
    # description
    description = db.Column(db.Text(1000), nullable=False)
    # timing
    starts_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ends_on = db.Column(db.DateTime, nullable=False)
    ## winning conditions ##
    # prize
    prize = db.Column(db.String(100), nullable=False)
    # winners
    n_winners = db.Column(db.Integer, nullable=False, default=1)
    submissions = relationship('Submission',
                            back_populates='competition',
                            lazy='dynamic',
                            cascade='all, delete, delete-orphan',
                            order_by='desc(Submission.timestamp) if True else Submission.timestamp')
                            # TODO: verify that this order_by works
    ## administrative ##
    active = db.Column(db.Boolean, nullable=False, default=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.code = generate_code(kwargs.get('name'))

    def __repr__(self):
        return f'<Competition {self.name} by {self.sponsor}>'

    @classmethod
    def get_active_competitions(cls):
        return cls.query.filter_by(active=True)

    def total_length(self):
        return (self.ends_on - self.starts_on).days

    def time_progressed(self):
        return (datetime.utcnow() - self.starts_on).days

    def time_remaining(self):
        return (self.ends_on - datetime.utcnow()).days

    def progressbar_width(self):
        total_length = self.total_length()
        if total_length==0:
            return f'width:100%;'
        return f'width: {100*float(self.time_progressed()/self.total_length())};'

    def winners(self):
        pass


class Submission(db.Model):
    __tablename__ = 'submission'
    # competition
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key=True)
    competition = relationship('Competition', back_populates='submissions')
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', back_populates='competition')
    ## post data ##
    # post time
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ## win data ##
    winner = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return (f'<Submission competition={self.competition.name} '
                f'project={self.project.name}>')
