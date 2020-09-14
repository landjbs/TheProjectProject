from datetime.datetime import utcnow
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Channel(CRUDMixin, db.Model):
    __tablename__ = 'channel'
    users = relationship('User',
                    secondary=user_to_channel,
                    lazy='dynamic')
    messages = relationship('Message',
        secondary=channel_to_message,
        lazy='dynamic',
        cascade='all, delete, delete-orphan',
        order_by='desc(Message.timestamp)')


class Message(CRUDMixin, db.Model):
    __tablename__ = 'message'
    from_id = None
    from_user = None
    to_id = None
    to_user = None
    # content
    text = db.Column(db.Text(128), unique=False, nullable=False)
    # metadata
    timestamp = db.Column(db.DateTime, nullable=False, default=utcnow)
