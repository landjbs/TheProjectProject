from application import db
from application.models import Project, User, Member_Role, Role

## CACHE ROLES ##
creator_role = db.session.query(Role).filter_by(name='Creator').first()
member_role = db.session.query(Role).filter_by(name='Member').first()


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


def add_role_to_project(project, role):
    a = Member_Role(role=role)
    a.project = project
    db.session.add(project)


def add_user_to_project(project, user, role):
    a = Member_Role(role=member_role)
    a.project = project
    user.projects.append(a)
    db.session.add(project)


def create_project(project, user):
    a = Member_Role(role=creator_role)
    a.project = project
    user.projects.append(a)
    db.session.add(project)


# projects = db.session.query(Member_Role.project_id).filter(Member_Role.user_id==None, Member_Role.role==role2)
# p = db.session.query(Project).filter(Project.id.in_(projects), Project.estimated_time>=11)
# for x in p:
#     print(x.name)
