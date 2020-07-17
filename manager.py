from application import db
from application.models import Project, User, Member_Role, Role

## CACHE ROLES ##
creator_role = db.session.query(Role).filter_by(name=='Creator').first()

def create_role(title, color):
    role = Role(title, color)
    db.session.add(role)
    db.session.commit()


def create_subject(name, color):
    subject = Subject(name, color)
    db.session.add(subject)
    db.session.commit()


def create_user(user):
    db.session.add(user)
    db.session.commit()


def create_project(project, user):
    add_user_to_project(user, project, creator_role)


def add_user_to_project(user, project, role):
    a = Member_Role(role)
    a.project = project
    user.projects.append(a)
    db.session.add(project)
