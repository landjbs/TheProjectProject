from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class Link(CRUDMixin, db.Model):
    __tablename__ = 'link'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # url
    url = db.Column(db.String(500), nullable=False, unique=False)
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project = relationship('Project', back_populates='links')

    def __repr__(self):
        return f'<Link {self.url}>'
