from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import db, CRUDMixin, generate_code
from app.project.models import Project


class Company(CRUDMixin, db.Model):
    __tablename__ = 'company'
    # __searchable__ = ['name']
    ##### DATA #####
    # name
    name = db.Column(db.String(128), nullable=False, unique=True)
    # code for url
    code = db.Column(db.String(128), nullable=False, unique=True)
    # oneliner
    oneliner = db.Column(db.String(40), nullable=False)
    # summary
    summary = db.Column(db.String(400), nullable=False)
    ## funding
    amount_raised = db.Column(db.Integer, nullable=True)
    looking_to_raise = db.Column(db.Boolean, nullable=False)
    ## team building
    looking_for_members = db.Column(db.Boolean, nullable=False)
    # application question
    application_question = db.Column(db.String(128), nullable=False)
    ## RELATIONSHIPS
    # users
    # NOTE: currently doesnt use Company_Role but maybe should in future
    # users = relationship('Company_Role',
                        # back_populates='company',
                        # lazy='dynamic',
                        # order_by='desc(Company_Role.joined_on)')
    members = relationship(
        'User',
        secondary='user_to_company',
        back_populates='companies'
    )
    # projects
    # projects = relationship(
    #     'Project',
    #     back_populates='company',
    #     cascade='all, delete, delete-orphan',
    #     order_by='desc(Project.last_active)'
    # )
    # competition
    # TODO: implement competiton submission for company maybe
    # last active
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(
        self,
        name,
        code,
        oneliner,
        summary,
        amount_raised,
        looking_to_raise,
        looking_for_members,
        application_question,
        members # TODO: replace owner with member list
    ):
        self.name                   =   str(name)
        self.code                   =   str(generate_code(name, Company))
        self.oneliner               =   str(oneliner)
        self.summary                =   str(summary)
        self.amount_raised          =   int(amount_raised)
        self.looking_to_raise       =   bool(looking_to_raise)
        self.looking_for_members    =   bool(looking_for_members)
        self.application_question   =   str(application_question)
        for member in members:
            self.members.append(member)


    @classmethod
    def build_from_form(cls, form, owner):
        data = form.data
        name                    = data.get('name')
        oneliner                = data.get('oneliner')
        summary                 = data.get('summary')
        amount_raised           = data.get('amount_raised', 0)
        looking_to_raise        = data.get('looking_to_raise')
        looking_for_members     = data.get('looking_for_members')
        application_question    = data.get('application_question')
        members = [owner]



# class Company_Role(db.Model):
#     __tablename__ = 'company_role'
#     # users
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#     user = relationship('User', back_populates='companies')
#     # company
#     company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
#     company = relationship('Company', back_populates='users')
#     # joined on
#     joined_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# class Company_Project(db.Model):
#     __tablename__ = 'company_project'
#     # project
#     project_id = db.Column(db.init_app, db.ForeignKey('project.id'), primary_key=True)
#     project = relationship('Project', back_populates='projects')
#     # company
#     company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
#     company = relationship('Company', back_populates='users')
