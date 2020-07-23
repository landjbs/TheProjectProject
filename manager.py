from application import db
from application.models import Project, User, Subject, User_Subjects


def create_subject(name, color):
    subject = Subject(name, color)
    db.session.add(subject)
    db.session.commit()


def create_user(user):
    db.session.add(user)


def add_subject_to_user(user, subject):
    prev = user.subjects.filter_by(subject=subject).first()
    if prev:
        prev.number += 1
    else:
        new = User_Subjects(user=user, subject=subject)
        user.subjects.append(new)
    return True


def add_user_to_project(project, user, role):
    user.projects.append(project)
    db.session.add(project)
    db.session.commit()


def create_project(project, user):
    user.projects.append(project)
    for subject in project.subjects:
        add_subject_to_user(user, subject)
    db.session.add(project)


def add_comment(project, user, comment):
    db.session.add(comment)


def add_task(project, user, task):
    db.session.add(task)


# projects = db.session.query(Member_Role.project_id).filter(Member_Role.user_id==None, Member_Role.role==role2)
# p = db.session.query(Project).filter(Project.id.in_(projects), Project.estimated_time>=11)
# for x in p:
#     print(x.name)
