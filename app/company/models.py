from app.database import db, CRUDMixin


class Company(CRUDMixin, db.Model):
    __tablename__ = 'company'
    __searchable__ = False
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(128), nullable=False, unique=True)
    users = relationship('User', )




class Company_Role(db.Model):
    __tablename__ = 'company_role'
    user = 
