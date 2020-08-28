from datetime import datetime

from app.database import db, CRUDMixin


class Company(CRUDMixin, db.Model):
    __tablename__ = 'company'
    __searchable__ = False
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(128), nullable=False, unique=True)
    users = relationship('Company_Role',
                        back_populates='companies',
                        cascade='delete-orphan',
                        order_by='desc(Company_Role.joined_on)')




class Company_Role(db.Model):
    __tablename__ = 'company_role'
    # users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='companies')
    # company
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
    company = relationship('Company', back_populates='users')
    # role
    role = db.Column(db.Text(128), nullable=True, unique=False)
    # joined on
    joined_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
