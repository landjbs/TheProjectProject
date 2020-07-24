from application import db
from application.models import Project, User, Subject, User_Subjects, Notification


def create_subject(name, color):
    subject = Subject(name, color)
    db.session.add(subject)
    db.session.commit()


def create_user(user):
    db.session.add(user)


## USER SUBJECTS ##
def add_subject_to_user(user, subject):
    prev = user.subjects.filter_by(subject=subject).first()
    if prev:
        prev.number += 1
    else:
        new = User_Subjects(user=user, subject=subject)
        user.subjects.append(new)
    return True


def remove_subject_from_user(user, subject):
    prev = user.subjects.filter_by(subject=subject).first()
    if prev:
        new_number = (prev.number - 1)
        if (new_number < 1):
            db.session.delete(prev)
        else:
            prev.number = new_number
    else:
        return False
    return True


## USER TO PROJECTS ##
def add_user_to_project(user, project):
    # add project subjects to user
    for subject in project.subjects:
        add_subject_to_user(user, subject)
    # notify all members
    notification = Notification(text=f'{user.name} has joined {project.name}.')
    for member in project.members:
        member.notifications.append(notification)
    # delete possible application
    application = project.pending_members.filter_by(user=user).first()
    if application is not None:
        db.session.delete(application)
    # delete possible invitation
    if user in project.invitations:
        project.invitations.remove(user)
    # add to session
    user.projects.append(project)
    db.session.add(project)
    db.session.commit()


def remove_user_from_project(user, project):
    # remove project subjects from user
    for subject in project.subjects:
        remove_subject_from_user(user, subject)
    # remove project from user projects
    user.projects.remove(project)
    # notify all remaining members
    notification = Notification(text=f'{user.name} has been removed from '
                                     f'{project.name} by the owner.')
    for member in project.members:
        if not member==user:
            member.notifications.append(notification)
    # notify removed member
    notification = Notification(text=f'You have been removed from '
                                     f'{project.name} by the owner. We promise '
                                     "it's nothing personal! Please contact us "
                                     'if you think something is wrong or have '
                                     'any questions.')
    user.notifications.append(notification)
    db.session.commit()
    return True


def delete_project(project):
    for member in project.members:
        for subject in project.subjects:
            remove_subject_from_user(member, subject)
    db.session.delete(project)
    db.session.commit()
    return True


def create_project(project, user):
    # add project subjects to user
    for subject in project.subjects:
        add_subject_to_user(user, subject)
    # add project to user projects
    user.projects.append(project)
    db.session.add(project)


def add_comment(project, user, comment):
    db.session.add(comment)


def add_task(project, user, task):
    db.session.add(task)


# projects = db.session.query(Member_Role.project_id).filter(Member_Role.user_id==None, Member_Role.role==role2)
# p = db.session.query(Project).filter(Project.id.in_(projects), Project.estimated_time>=11)
# for x in p:
#     print(x.name)
