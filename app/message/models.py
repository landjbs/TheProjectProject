from datetime.datetime import utcnow
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Channel(CRUDMixin, db.Model):
    __tablename__ = 'channel'
    users = relationship('User',
                    secondary=user_to_channel,
                    lazy='dynamic')
    messages = relationship('Message',
        back_populates='channel',
        lazy='dynamic',
        cascade='all, delete, delete-orphan',
        order_by='desc(Message.timestamp)')
    last_active = db.Column(db.DateTime, nullable=False, default=utcnow)


class Message(CRUDMixin, db.Model):
    __tablename__ = 'message'
    # sender
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = relationship('User', back_populates='messages')
    # channel
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = relationship('Channel', back_populates='messages')
    # content
    text = db.Column(db.Text(128), unique=False, nullable=False)
    # metadata
    timestamp = db.Column(db.DateTime, nullable=False, default=utcnow)
