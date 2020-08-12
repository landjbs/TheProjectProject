from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Question(CRUDMixin, db.Model):
    __tablename__ = 'question'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', back_populates='questions')
    # question
    question = db.Column(db.String(100), nullable=False, unique=False)
    # answer
    answer = db.Column(db.String(500), nullable=True, unique=False)

    def __repr__(self):
        return(f'<Question_Answer q={self.question} a={self.answer} '
            f'p={self.project.name}>')

    def is_answered(self):

    def add_answer(self, answer):
        self.answer = answer
        self.update()
