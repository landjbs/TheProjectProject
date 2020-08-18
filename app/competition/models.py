from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin, generate_code



class Competition(CRUDMixin, db.Model):
    __tablename__ = 'competition'
    # __searchable__ = ['name', 'sponsor']
    # name
    name = db.Column(db.String(128), nullable=False)
    # code
    code = db.Column(db.String(128), nullable=False, unique=True)
    # sponsor
    sponsor = db.Column(db.String(400), nullable=False, default='<a href="/">TheProjectProject</a>')
    # oneliner
    oneliner = db.Column(db.String(100), nullable=False)
    # description
    description = db.Column(db.Text(1000), nullable=False)
    # timing
    starts_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ends_on = db.Column(db.DateTime, nullable=False)
    ## winning conditions ##
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
        ''' Gets winning submissions if competion is over '''
        if not self.complete:
            return None
        return self.submissions.filter_by(winner=True)

    ## admin ##
    def select_winners(self, winner_ids):
        ''' Selects winners for competition using project id '''
        assert self.active, 'Cannot select winners for inactive competition.'
        assert not self.complete, 'Cannot select winners for compelte competition.'
        n_selected = len(winner_ids)
        assert (n_selected==self.n_winners), (f'Invalid winner number '
                                            f'{n_selected}/{self.n_winners}.')
        winning_projects = []
        # first loop to make sure no errors before starting actions
        for id in winner_ids:
            winner = self.submissions.filter_by(project_id=id).first()
            if not winner:
                raise ValueError(f'Project with id {id} has not submitted.')
            winning_projects.append(winner)
        # notify winning project members
        for winner in winning_projects:
            winner.winner = True
            winner.project.buzz += 10
            winner.project.notify_members(text=('Congratulations—your project '
                    f'{winner.name} has won the competition {self.name}! '
                    'We were really impressed by your work and will follow up '
                    'soon with instructions for claiming your reward!'),
                    important=True)
        # notify other members
        for submission in self.submissions:
            project = submission.project
            if not project in self.winners:
                project.notify_members(text=(f'The competition {self.name}'
                    'has come to an end! We had some awesome submissions—'
                    f'{project.name} included. While we were really impressed '
                    'with your work, we have not selected you as a winner this '
                    'time around. This if far from the end of the world—'
                    f'you can certainly keep working on {project.name}, and we '
                    'may still be able to connect you with resources and '
                    'publicity on our social media accounts!')
                )
        self.active = False
        self.complete = True
        self.update()
        return True


class Submission(CRUDMixin, db.Model):
    __tablename__ = 'submission'
    # competition
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
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
