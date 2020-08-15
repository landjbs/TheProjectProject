from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin



class Hackathon(CRUDMixin, db.Model):
    __tablename__ = ''
    # id
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(100), nullable=False)
    # sponsor
    sponsor = db.Column(db.String(100), nullable=True)
    # description
    description = db.Column(db.Text(), nullable=False)
    # prize
    prize = db.Column(db.String(100), nullable=False)
    # timing
    starts_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ends_on = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Hackathon {self.name} by {self.sponsor}>'

    def time_progressed(self):
        return (datetime.utcnow() - self.starts_on).days

    def time_remaining(self):
        return (self.ends_on - datetime.utcnow()).days
