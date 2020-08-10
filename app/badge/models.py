from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin

from .badge_criteria import badge_criteria


class Badge(CRUDMixin, db.Model):
    __tablename__ = 'badge'
    # id
    id = db.Column(db.Integer, primary_key=True)
    ## display ##
    # name
    name = db.Column(db.String(60), nullable=False, unique=True)
    # url for icon
    icon = db.Column(db.String(250), nullable=False, unique=True)
    # description
    description = db.Column(db.String(250), nullable=False)
    # perks
    perks = relationship('Badge_Perk',
                         back_populates='badge',
                         cascade='all, delete, delete-orphan',
                         lazy='dynamic')
    ## evaluation ##
    # criteria
    criteria = db.Column(db.Integer, nullable=False)
    # evaluator: user attr to call for progress
    evaluator = db.Column(db.String(50), nullable=False)
    # users
    users = relationship('User_Badge',
                        back_populates='badge',
                        cascade='all, delete, delete-orphan',
                        lazy='dynamic',
                        order_by='User_Badge.earn_stamp')

    def __init__(self, name, icon, description, perks, criteria, evaluator):
        self.name = name
        self.icon = icon
        self.description = description
        self.criteria = criteria
        self.evaluator = evaluator
        # add perks
        for perk in perks:


    def __repr__(self):
        return f'<Badge {self.name}>'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


class User_Badge(CRUDMixin, db.Model):
    __tablename__ = 'user_badge'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=False)
    user = relationship('User', back_populates='badges')
    # badges
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), primary_key=False)
    badge = relationship('Badge', back_populates='users')
    # progress
    progress = db.Column(db.Integer, nullable=False, default=0)
    # earn
    earned = db.Column(db.Boolean, nullable=False, default=False)
    earn_stamp = db.Column(db.DateTime, nullable=True)
    # last active: last time progress was made on the badge
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, badge):
        self.badge = badge

    def __repr__(self):
        if not self.earned:
            return (f'<User_Badge u={self.user.name} b={self.badge.name}'
                    f'progress={self.progress}/{self.badge.criteria}>')
        else:
            return (f'<User_Badge u={self.user.name} b={self.badge.name}'
                    f'earned={self.earn_stamp}>')

    def fraction_complete(self):
        ''' Get fraction of badge completedness '''
        return float(self.progress / self.badge.criteria)

    def get_progressbar_width(self):
        ''' Gets width of progressbar for badge display '''
        return f'width: {100*min(1, self.fraction_complete())}%;'

    def update_last_active(self):
        ''' Doesnt commit '''
        self.last_active = datetime.utcnow()
        return True

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
                self.update_last_active()
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
                self.update_last_active()
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


class Badge_Perk(CRUDMixin, db.Model):
    __tablename__ = 'badge_perk'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(60), nullable=False, unique=True)
