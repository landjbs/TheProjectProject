from application import db
from application.models import Project, User, Member_Role, Role

## CACHE ROLES ##
creator_role = db.session.query(Role).filter_by(name=='Creator').first()

def create_role(title, color):
    db.session.add(Role(title, color))
    db.session.commit()


def create_subject(name, color):
    db.session.add(Subject(name, color))
    db.session.commit()


def create_user(user):
    db.session.add(user)
    db.session.commit()


def create_project(project, user):
    a = Member_Role(creator_role)
    a.project = project
    user.projects.append(a)
    db.session.add(project)


def add_user_to_project(user, project, role):
    a = Member_Role(role)
    a.project = project
    user.projects.append(a)
