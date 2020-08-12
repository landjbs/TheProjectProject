from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Question(CRUDMixin, db):
    __tablename__ = 'question'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # text
    text = db.Column(db.String(100), nullable=True, unique=True)


class Answer(CRUDMixin, db):
    __tablename__ = 'answer'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # answer
    answer = db.Column(db.String(500), nullable=True)
