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
    total = db.Column(db.Integer, nullable=False)
    # earn
    earned = db.Column(db.Boolean, nullable=False, default=False)
    earn_stamp = db.Column(db.DateTime, nullable=True)

    def __init__(self, badge, progress, total):
        self.badge = badge
        self.progress = progress
        self.total = total
        # mark earned if deserved
        if progress>=total:
            self.mark_earned()


    def __repr__(self):
        if not self.earned:
            return (f'<User_Badge u={self.user.name} b={self.badge.name}'
                    f'p={self.progress}>')
        else:
            return (f'<User_Badge u={self.user.name} b={self.badge.name}'
                    f'e={self.earn_stamp}>')

    def fraction_complete(self):
        ''' Get fraction of badge completedness '''
        return float(self.progress / self.total)

    def get_progressbar_width(self):
        ''' Gets width of progressbar for badge display '''
        return f'width: {100*min(1, self.fraction_complete())}%;'

    def update_progress(self, progress, total):
        ''' Updates progress on badge by inc '''
        self.progress = progress
        self.total = total

        self.update()
        return True

    def mark_earned(self):
        ''' Marks badge as earned and tracks time of earning '''
        self.earn_stamp = datetime.utcnow()
        self.earned = True
        self.update()
        return True
