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
    a = Member_Role(roles=[role])
    a.project = project
    db.session.add(project)


def add_user_to_project(project, user, role):
    a = Member_Role(roles=[role])
    a.project = project
    user.projects.append(a)
    db.session.add(project)
    db.session.commit()


def add_role_to_user(project, user, role):
    member_role = user.projects.filter_by(id=project.id).first()
    if not role in member_role.roles:
        member_role.roles.append(role)
    db.session.add(member_role)
    db.session.commit()


def create_project(project, user):
    a = Member_Role(roles=[db.session.query(Role).filter_by(name='Creator').first()])
    a.project = project
    user.projects.append(a)
    db.session.add(project)


def add_comment(project, user, comment):
    db.session.add(comment)


def add_task(project, user, task):
    db.session.add(task)

# projects = db.session.query(Member_Role.project_id).filter(Member_Role.user_id==None, Member_Role.role==role2)
# p = db.session.query(Project).filter(Project.id.in_(projects), Project.estimated_time>=11)
# for x in p:
#     print(x.name)
