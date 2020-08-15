from datetime import datetime
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin


class Notification(CRUDMixin, db.Model):
    __tablename__ = 'notification'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # text
    text = db.Column(db.String(160), nullable=False)
    # important
    important = db.Column(db.Boolean, nullable=False, default=False)
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='notifications')
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project = relationship('Project', back_populates='notifications')
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
