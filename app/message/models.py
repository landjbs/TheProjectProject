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

    def send(self, body, sender):
        ''' Sends message of body from sender to channel '''
        if not sender in self.users:
            return False
        self.messages.append(Message(body=body, sender=sender))
        self.last_active = utcnow()
        self.update()
        return True


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


class User_Channel(db.Model):
    __tablename__ = 'user_channel'
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='channels')
    # channel
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), primary_key=True)
    channel = relationship('Channel', back_populates='users')
    # last read (last time user read channel)
    last_read = db.Column(db.DateTime, nullable=False, default=utcnow)

    def n_new(self):
        last_read = self.last_read
        return self.channel.filter(last_active>last_read)
