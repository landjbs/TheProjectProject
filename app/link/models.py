from datetime import datetime
from sqlalchemy.orm import relationship

import .embedder

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
    ## render data (potentially should be moved somewhere more efficient) ##
    title = db.Column(db.String(500), nullable=True, unique=False)
    description = db.Column(db.Text(), nullable=True, unique=False)
    is_rendered = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, url):
        self.url = url
        scape_data = embedder.scrape(url)
        ## load page data ##
        self.title = scape_data['title']
        self.description = scape_data['description']
        self.is_rendered = True

    def __repr__(self):
        return f'<Link {self.url}>'
