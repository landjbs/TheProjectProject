from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Question(CRUDMixin, db):
    __tablename__ = 'question'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # question
    question = db.Column(db.String(100), nullable=True, unique=True)
    # answers
    answers = relationship('Question_Answer', back_populates='question')

    def __repr__(self):
        return f'<Question {self.question}>'


class Question_Answer(CRUDMixin, db):
    __tablename__ = 'answer'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # question
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = relationship('Question', back_populates='answers')
    # answer
    answer = db.Column(db.String(500), nullable=True, unique=False)
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', back_populates='answers')

    def __repr__(self):
        return f'<{self.question}<Answer {self.text}>>'
