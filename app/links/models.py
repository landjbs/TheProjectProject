from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin


class ULR(CRUDMixin, db.Model):
    __tablename__ = 'url'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # url
    url = db.Column(db.String(500), nullable=False, unique=True)
    # 
