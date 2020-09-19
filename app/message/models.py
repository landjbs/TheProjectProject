from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Channel(CRUDMixin, db.Model):
    __tablename__ = 'channel'
    users = relationship('User_Channel',
                    lazy='dynamic',
                    cascade='all, delete, delete-orphan',
                    back_populates='channel')
    messages = relationship('Message',
        back_populates='channel',
        lazy='dynamic',
        cascade='all, delete, delete-orphan',
        order_by='desc(Message.timestamp)')
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return (f'<Channel '
                f'n_user={self.users.count()} '
                f'n_messages={self.messages.count()} '
                f'last_active={self.last_active}>')

    # classmethods
    @classmethod
    def new(cls, users):
        ''' Creates new channel with users unless already exists '''
        if len(users)!=2:
            raise NotImplementedError('Support for channels w !=2 members.')
        # search for previously existing instance of channel
        if False:
            raise NotImplementedError('')
        else:
            # create channel
            channel = Channel()
            for user in users:
                channel.users.append(User_Channel(user=user, channel=channel))
            channel.update()
        return channel

    # permissions
    def is_member(self, user):
        # WARNING: MUST BE IMPLEMENTED
        return True

    # actions
    def send(self, text, sender):
        '''
        Sends message of text from sender to channel. Returns message if sent.
        '''
        if self.users.filter_by(user=sender).first() is None:
            return False
        message = Message(text=text, sender=sender)
        self.messages.append(message)
        self.last_active = datetime.utcnow()
        self.update()
        return message

    def name(self, me):
        ''' Generates user-specific name for the channel '''
        users = set([uc.user for uc in self.users if uc.user!=me])
        name = ''
        for i, user in enumerate(users):
            if (i>0):
                name += ', '
            name += user.name
        return name


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
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message "{self.text}" by {self.sender} on {self.timestamp}>'


class User_Channel(db.Model):
    __tablename__ = 'user_channel'
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='channels')
    # channel
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), primary_key=True)
    channel = relationship('Channel', back_populates='users')
    # last read (last time user read channel)
    last_read = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<User_Channel links {self.user} with {self.channel}>'

    def n_new(self):
        last_read = self.last_read
        return self.channel.filter(last_active>last_read)
