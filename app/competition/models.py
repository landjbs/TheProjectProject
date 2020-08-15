from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin



class Competition(CRUDMixin, db.Model):
    __tablename__ = 'competition'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(100), nullable=False)
    # sponsor
    sponsor = db.Column(db.String(100), nullable=False, default='TheProjectProject')
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
    projects = relationship('Project',
                        secondary='competition_to_project',
                        back_populates='competitions')
    ## administrative ##
    active = db.Column(db.Boolean, nullable=False, default=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Competition {self.name} by {self.sponsor}>'

    @classmethod
    def get_active_competitions(cls):
        return cls.filter_by(active=True)

    def time_progressed(self):
        return (datetime.utcnow() - self.starts_on).days

    def time_remaining(self):
        return (self.ends_on - datetime.utcnow()).days

    def progressbar_width(self):
        return f'width: {100*float(self.time_progressed()/self.ends_on)};'

    def add_winner(self, project):
        ''' Adds winner project '''
        self.winners.append(project)
        winner_note = (f'Congratulations!! You have won the {self.name} '
                    'competition!')
        project.notify_members(winner_note)
        return True
