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
        channel = cls.get_by_users(users)
        if channel is None:
            print("HERE")
            channel = Channel()
            for user in users:
                channel.users.append(User_Channel(user=user, channel=channel))
            channel.update()
        print(channel)
        return channel

    @classmethod
    def get_by_users(cls, users):
        ''' Gets chat comprised of exactly of all users. none if none '''
        # TODO: implement sql query to speed way up. pretty important
        # get all channels shared across all users
        shared = set()
        for i, user in enumerate(users):
            user_set = set(uc.channel for uc in user.channels)
            if i==0:
                shared = user_set
            else:
                shared = shared.intersection(user_set)
        n_shared = len(shared)
        if n_shared==0:
            return None
        elif n_shared==1:
            return next(iter(shared))
        else:
            u_num = len(users)
            for channel in shared:
                if channel.users.count()==u_num:
                    return channel
            raise None
        raise NotImplementedError('bug')

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

    # data
    def most_recent(self):
        ''' Get send time of most recent message '''
        if self.messages.count()>0
            return self.messages[0].timestamp
        else:
            return 0

    def data(self):
        ''' Gets dict of data about channel for rendering '''
        if self.messages.count()>0:
            return {'last_sent' : self.most_recent()}
        return {'last_sent' : False}

    # user-specific
    def name(self, me):
        ''' Generates user-specific name for the channel '''
        users = set([uc.user for uc in self.users if uc.user!=me])
        name = ''
        for i, user in enumerate(users):
            if (i>0):
                name += ', '
            name += f'<a class="owner" href="{user.get_url()}">{user.name}</a>'
        return name

    def n_unseen(self, user):
        # get last read from user channel
        last_read = self.users.filter_by(user=user).first().last_read
        return self.messages.filter(Message.timestamp>last_read).count()


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
