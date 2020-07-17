from application import db
from application.models import Project, User, Member_Role, Role


def create_role(title, color):
    db.session.add(Role(title, color))
    db.session.commit()


def create_subject(name, color):
    db.session.add(Subject(name, color))
    db.session.commit()
