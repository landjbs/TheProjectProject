from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import db, CRUDMixin
from app.project.models import Project


class Company(CRUDMixin, db.Model):
    __tablename__ = 'company'
    # __searchable__ = ['name']
    # name
    name = db.Column(db.String(128), nullable=False, unique=True)
    # code for url
    code = db.Column(db.String(128), nullable=False, unique=True)
    # oneliner
    oneliner = db.Column(db.String(40), nullable=False)
    # summary
    summary = db.Column(db.String(400), nullable=False)
    # users
    users = relationship('Company_Role',
                        back_populates='companies',
                        order_by='desc(Company_Role.joined_on)')
    # projects
    projects = relationship('Company_Project',
                            back_populates='companies',
                            order_by='desc(Company_Project.)')
    # last active
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Company_Role(db.Model):
    __tablename__ = 'company_role'
    # users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='companies')
    # company
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
    company = relationship('Company', back_populates='users')
    # joined on
    joined_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Company_Project(db.Model):
    __tablename__ = 'company_project'
    # project
    project_id = db.Column(db.init_app, db.ForeignKey('project.id'), primary_key=True)
    project = relationship('Project', back_populates='projects')
    # company
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
    company = relationship('Company', back_populates='users')
    # salary
    salary = db.Column(db.Integer, nullable=False, default=0)
