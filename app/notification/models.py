from datetime import datetime
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin


class Notification(CRUDMixin, db.Model):
    __tablename__ = 'notification'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # text
    text = db.Column(db.String(160), nullable=False)
    # category {0:neutral, 1:success, 2:warning: 3:important}
    category = db.Column(db.Integer, nullable=True)
    # user
    # TODO: change to single user to notification 
    users = relationship('User', secondary='user_to_notification',
                         back_populates='notifications')
    # timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # marks seen
    seen = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Notification to {self.users} at {self.timestamp}; TEXT={self.text}>'

    def mark_seen(self):
        self.seen = True
        self.update()
        return True
