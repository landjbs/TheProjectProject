from datetime import datetime
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin


class Notification(CRUDMixin, db.Model):
    __tablename__ = 'notification'
    # text
    text = db.Column(db.String(160), nullable=False)
    # important
    important = db.Column(db.Boolean, nullable=False, default=False)
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='notifications')
    # redirect
    redirect = db.Column(db.String(128), nullable=True)
    # timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # marks seen
    seen = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Notification at {self.timestamp}; TEXT={self.text}>'

    def mark_seen(self):
        self.seen = True
        self.update()
        return True
