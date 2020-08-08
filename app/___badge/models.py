from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin


## BASE CLASSES ##
class Badge(CRUDMixin, db.Model):
    __tablename__ = 'badge'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(60), nullable=False, unique=True)
    # url for icon
    icon_url = db.Column(db.String(250), nullable=False, unique=True)
    # color
    color = db.Column(db.String(6), unique=True, nullable=False)
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
    earned = db.Column(db.Boolean, nullable=False, default=False)
    earn_stamp = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        if not self.earned:
            return f'<User_Badge u={self.user.name} b={self.badge.name} p={self.progress}>'
        else:
            return f'<User_Badge u={self.user.name} b={self.badge.name} e={self.earn_stamp}>'
