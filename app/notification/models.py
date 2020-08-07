from datetime import datetime
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin


class Notification(CRUDMixin, db.Model):
    __tablename__ = 'notification'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # text
    text = db.Column(db.String(160), nullable=False)
    # user
    users = relationship('User', secondary=user_to_notification,
                         back_populates='notifications')
    # timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Notification to {self.users} at {self.timestamp}; TEXT={self.text}>'
