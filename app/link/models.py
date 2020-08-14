from datetime import datetime
from sqlalchemy.orm import relationship

from .embedder import scrape

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
    # is link public
    public = db.Column(db.Boolean, nullable=False, default=True)
    # category within project: {1:repo, 2:communication, 3:drive: 4:management, 5:other}
    # category = db.Column(db.Integer, nullable=False, default=0)
    ## render data (potentially should be moved somewhere more efficient) ##
    description = db.Column(db.Text(100000), nullable=True, unique=False)
    is_rendered = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, url, public, category):
        self.url = url
        # self.public = public
        # self.category = category
        scape_data = scrape(url)
        ## load page data ##
        self.description = str(scape_data['description'])
        self.is_rendered = True

    def __repr__(self):
        return f'<Link {self.url}>'
