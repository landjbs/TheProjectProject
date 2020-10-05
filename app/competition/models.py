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
                            order_by='desc(Submission.timestamp)')
    ## administrative ##
    active = db.Column(db.Boolean, nullable=False, default=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Competition {self.name} by {self.sponsor}>'

    def get_url(self):
        return f'/competition={self.code}'

    @classmethod
    def get_active_competitions(cls):
        return cls.query.filter_by(active=True)

    @classmethod
    def recommend(cls):
        # TODO: move this to recommendation engine
        competitions = cls.query.filter_by(active=True, complete=False)
        return [('', '')] + [(c.id, f'<u>{c.name}</u><br>{c.oneliner}') for c in competitions]

    def total_length(self):
        return (self.ends_on - self.starts_on).days

    def time_progressed(self):
        now = datetime.utcnow()
        starts_on = self.starts_on
        ends_on = self.ends_on
        if starts_on > now:
            return 0
        elif now > ends_on:
            return int((ends_on - starts_on).days)
        return int((datetime.utcnow() - self.starts_on).days)

    def time_remaining(self):
        return (self.ends_on - datetime.utcnow()).days

    def progressbar_width(self):
        total_length = self.total_length()
        if total_length==0:
            return f'width:100%;'
        return f'width: {100*float(self.time_progressed()/self.total_length())}%;'

    def winners(self):
        ''' Gets winning submissions if competition is over '''
        if not self.complete:
            return None
        return self.submissions.filter_by(winner=True)

    def ordered_submissions(self):
        ''' Returns projects submitted with winners first and then chronological '''
        winners = self.submissions.filter_by(winner=True)
        winner_ids = [s.project.id for s in winners]
        others = self.submissions.filter(~Submission.project_id.in_(winner_ids))
        return (winners.all() + others.all())

    ## admin ##
    def activate(self):
        # assertions
        assert not self.active, 'Already active.'
        assert not self.complete, 'Already complete.'
        assert not (datetime.utcnow() > self.ends_on), 'Invalid end date.'
        # make active
        self.active = True
        # notify relevant users
        # NOTE: potentially only recommend to certain users in future
        from app.user.models import User
        User.notify_all(
            text=(f'{self.name}, a new competition you might like, just went '
                  'live! Click here to join—good luck!'),
            name=self.name,
            important=True,
            redirect=self.get_url()
        )
        return True

    def start_judging(self):
        assert self.active, 'Cannot complete inactive competition.'
        assert not self.complete, 'Cannot judge competition that is already completed'
        assert not (self.ends_on > datetime.utcnow()), 'Cannot judge competition with future end date.'
        self.active = False
        self.complete = True
        for submission in self.submissions:
            submission.project.notify_members(
                text=(f'The competition "{self.name}" has come to an end and the '
                'judging process has begun. We will release the results soon— '
                'stay tuned!'
                )
            )
        self.update()


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

    def mark_winner(self):
        competition = self.competition
        # validate that competition meets criteria for new winner
        assert not competition.active, 'Cannot select winners for active competition.'
        assert competition.complete, 'Cannot select winners for incomplete competition.'
        # get number of prev winners in competition
        n_prev = competition.submissions.filter_by(winner=True).count()
        assert n_prev<=competition.n_winners, f'Cannot have more than n_winners'
        # mark submission as winner
        self.winner = True
        # update project buzz
        self.project.buzz += 10
        # notify project members
        self.project.notify_members(text=('Congratulations—your project '
                f'"{self.project.name}" has won the competition "{competition.name}"! '
                'We were really impressed by your work and will follow up '
                'soon with instructions for claiming your reward!'),
                important=True)
        self.update()
        return True

    def mark_loser(self):
        competition = self.competition
        # validate that competition meets criteria for new winner
        assert not competition.active, 'Cannot select winners for active competition.'
        assert competition.complete, 'Cannot select winners for incomplete competition.'
        # mark submission as loser
        self.winner = False
        # notify project members
        project = self.project
        project.notify_members(text=(f'We have finished judging submissions '
            f'for the competition "{competition.name}". While we were really impressed '
            'with your work, we have not selected you as a winner this '
            'time around. This if far from the end of the world—'
            f'you should certainly keep working on {project.name}, and we '
            'may still be able to connect you with resources and '
            'publicity on our social media accounts!')
        )
        self.update()
        return True
