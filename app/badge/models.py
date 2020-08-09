from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin

from .badge_criteria import badge_criteria



class Badge(CRUDMixin, db.Model):
    __tablename__ = 'badge'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(60), nullable=False, unique=True)
    # url for icon
    icon = db.Column(db.String(250), nullable=False, unique=True)
    # criteria
    criteria = db.Column(db.Integer, nullable=False)
    # evaluator: user attr to call for progress
    evaluator = db.String(db.String(50), nullable=False)
    # users
    users = relationship('User_Badge',
                        back_populates='badge',
                        cascade='all, delete, delete-orphan',
                        lazy='dynamic',
                        order_by='User_Badge.earn_stamp')

    def __repr__(self):
        return f'<Badge {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def get_criteria(self):
        ''' Gets criteria and evaluator for badge from badge_criteria '''
        return badge_criteria.get_criteria(self.name)


class User_Badge(db.Model):
    __tablename__ = 'user_badge'
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='badges')
    # badges
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), primary_key=True)
    badge = relationship('Badge', back_populates='users')
    # progress
    progress = db.Column(db.Integer, nullable=False, default=0)
    # earn
    earned = db.Column(db.Boolean, nullable=False, default=False)
    earn_stamp = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        if not self.earned:
            return (f'<User_Badge u={self.user.name} b={self.badge.name}'
                    f'progress={self.progress}/{self.badge.total}>')
        else:
            return (f'<User_Badge u={self.user.name} b={self.badge.name}'
                    f'earned={self.earn_stamp}>')

    def fraction_complete(self):
        ''' Get fraction of badge completedness '''
        return float(self.progress / self.badge.total)

    def get_progressbar_width(self):
        ''' Gets width of progressbar for badge display '''
        return f'width: {100*min(1, self.fraction_complete())}%;'

    def update_progress(self):
        ''' Updates progress on badge '''
        # get user progress using evaluator
        self.progress = int(getattr(self.user, self.badge.evaluator)())
        # get total from badge
        self.total = self.badge.criteria
        # if user deserves badge...
        if (self.progress>=self.total):
            # and hasn't been awarded it...
            if not self.earned:
                # mark as earned (which autoupdates)
                self.mark_earned()
        # if user doesn't deserve badge...
        else:
            # and has been awarded it...
            if self.earned:
                # remove earned (which autoupdates)
                self.remove_earned_marking()
            # and hasn't been awarded it...
            else:
                # just update progress
                self.update()
        return True

    def mark_earned(self):
        ''' Marks badge as earned and tracks time of earning '''
        if not self.earned:
            # stamp time of earning
            self.earn_stamp = datetime.utcnow()
            # set earned to true
            self.earned = True
            # notify user
            self.user.notify(text=('Congratulations—you have won the '
                                   f'{self.badge} badge!'),
                             category=1)
            self.update()
            return True
        return False

    def remove_earned_marking(self):
        ''' Removes badge if earned'''
        if self.earned:
            # remove earn stamp and set earned to false
            self.earn_stamp = None
            self.earned = False
            # notify the user
            self.user.notify(text=('Due to changes to your account (eg. left '
                                   'projects or deleted tasks), you no longer '
                                   'meet the threshold for the '
                                   f'{self.badge.name} badge.'),
                            category=0)
            self.update()
            return True
        return False
