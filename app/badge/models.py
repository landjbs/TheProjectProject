from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin



class Badge(CRUDMixin, db.Model):
    __tablename__ = 'badge'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(60), nullable=False, unique=True)
    # url for icon
    icon = db.Column(db.String(250), nullable=False, unique=True)
    # users
    users = relationship('User_Badge',
                        back_populates='badge',
                        cascade='all, delete, delete-orphan',
                        lazy='dynamic',
                        order_by='User_Badge.earn_stamp')

    def __repr__(self):
        return f'<Badge {self.name}>'



class User_Badge(db.Model):
    __tablename__ = 'user_badge'
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='badges')
    # badges
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), primary_key=True)
    badge = relationship('Badge', back_populates='users')
    # progress
    progress = db.Column(db.Float, nullable=False, default=float(0))
    total = db.Column(db.Integer, nullable=False)
    # earn
    earned = db.Column(db.Boolean, nullable=False, default=False)
    earn_stamp = db.Column(db.DateTime, nullable=True)

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

    def update_progress(self, inc=1):
        ''' Updates progress on badge by inc '''
        if self.earned:
            return False
        self.progress += inc
        if self.progress==self.total:
            self.mark_earned()
        else:
            self.update()
        return True

    def mark_earned(self):
        ''' Marks badge as earned and tracks time of earning '''
        self.earn_stamp = datetime.utcnow()
        self.earned = True
        self.update()
        return True
