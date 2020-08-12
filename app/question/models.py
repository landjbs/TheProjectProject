from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Question_Answer(CRUDMixin, db.Model):
    __tablename__ = 'question_answer'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', back_populates='answers')
    # question
    question = db.Column(db.String(100), nullable=False, unique=False)
    # answer
    answer = db.Column(db.String(500), nullable=True, unique=False)

    def __repr__(self):
        return f'<Question_Answer q={self.question} a={self.answer} p={self.project.name}>'

    def answer(self, answer):
        self.answer = answer
        self.update()
