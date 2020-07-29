from flask import flash

from application import db
from application.models import Project, User, Subject, User_Subjects, Notification


def create_subject(name, color):
    subject = Subject(name, color)
    db.session.add(subject)
    db.session.commit()


## USER ##
def create_user(user, subject_ids):
    db.session.add(user)
    for id in subject_ids:
        subject = Subject.query.get(id)
        if subject:
            add_subject_to_user(user, subject)
    db.session.add(user)
    db.session.commit()
    return True


## USER SUBJECTS ##
def add_subject_to_user(user, subject):
    prev = user.subjects.filter_by(subject=subject).first()
    if prev is not None:
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


def delete_user(user):
    # delete user/subject associations
    for s in user.subjects:
        db.session.delete(s)
    # delete user notifications
    for notification in user.notifications:
        db.session.delete(notification)
    # delete incomplete user authored tasks and transfer complete to anonymous
    for task in user.tasks_authored:
        if task.complete==False:
            db.session.delete(task)
        else:
            task.author = None
    # delete applications submitted by user
    for application in user.pending:
        delete_application(application)
    # delete invitations extended to user
    for invitation in user.invitations:
        db.session.delete(invitation)
    # delete comments posted by user
    for comment in user.comments:
        db.session.delete(comment)
    db.session.delete(user)
    db.session.commit()


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
    application = project.pending.filter_by(user=user).first()
    if application is not None:
        db.session.delete(application)
    # delete possible invitation
    if user in project.invitations:
        project.invitations.remove(user)
    # delete possible rejection
    if user in project.rejections:
        project.rejections.remove(user)
    # add to session
    user.projects.append(project)
    db.session.add(project)
    db.session.commit()
    return True


def remove_user_from_project(user, project, admin=False):
    ''' admin: true if owner removed false if user '''
    # remove project subjects from user
    for subject in project.subjects:
        remove_subject_from_user(user, subject)
    # remove project from user projects
    user.projects.remove(project)
    # notify all members depending on manner of removal
    if admin:
        member_note = Notification(text=f'{user.name} has been removed from '
                                         f'{project.name} by the owner.')
        rem_note = Notification(text=f'You have been removed from '
                                     f'{project.name} by the owner. We promise '
                                     "it's nothing personal! Please contact us "
                                     'if you think something is wrong or have '
                                     'any questions.')
        user.notifications.append(rem_note)
        flash(f'You have removed {user.name} from {project.name}.')
    else:
        member_note = Notification(text=f'{user.name} has left '
                                        f'{project.name}.')
    for member in project.members:
        if not member in [user, project.owner]:
            member.notifications.append(member_note)
    # add rejection to user and project
    user.rejections.append(project)
    # add to session
    db.session.commit()
    return True


def reject_user_from_pending(user, project, admin=True):
    ''' Rejects user with pending application to project '''
    application = project.pending.filter_by(user=user).first()
    if application is None:
        flash(f'Cannot reject {user.name} application to {project.name} '
               "because they haven't applied.")
        return False
    db.session.delete(application)
    # notify rejected user if admin rejected
    if admin:
        notifcation = Notification(text=f'The owner of {project.name} decided not '
                                         'to add you to the project right now. '
                                         "We promise it's nothing personal! "
                                         'Please contact us if you think something'
                                         ' is wrong or have any questions.')
        user.notifications.append(notifcation)
        flash(f'You have rejected {user.name} from {project.name}.')
    # remove all unseen pertinent notifications from owner
    else:
        for note in project.owner.notifications:
            if (user.name in note.text) and (project.name in note.text):
                project.owner.notifications.remove(note)
    # add rejection to user and project
    user.rejections.append(project)
    db.session.commit()
    return True


def reject_project_invitation(user, project, admin):
    ''' admin: true if rejected by project owner '''
    if not user in project.invitations:
        return False
    # remove invitation
    project.invitations.remove(user)
    # add rejection to user and project
    user.rejections.append(project)
    # notify project owner
    if not admin:
        notification = Notification(text=(f'{user.name} has decided '
                                    f'not to collaborate on {project.name}. '
                                    "We promise it's nothing personal! Please "
                                    'contact us if you think a mistake was made.'))
        project.owner.notifications.append(notification)
        flash(f'You have declined the offer to collaborate on {project.name}.')
    else:
        flash(f'You have withdrawn your invitation of {user.name} to {project.name}.')
        # remove invitation from user notifcations
        for note in user.notifications:
            if project.name in note.text:
                user.notifications.remove(note)
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


def open_project(project):
    if not project.open:
        project.open = True
        note = Notification(text=f'{project.name} has been opened by the owner.')
        for member in project.members:
            if not member==project.owner:
                member.notifcations.append(note)
    db.session.commit()
    flash(f'You have opened {project.name}.')
    return True


def close_project(project):
    if project.open:
        project.open = False
        note = Notification(text=f'{project.name} has been closed by the owner.')
        for member in project.members:
            if not member==project.owner:
                member.notifcations.append(note)
    db.session.commit()
    flash(f'You have closed {project.name}.')
    return True


def add_comment(project, user, comment):
    db.session.add(comment)


def add_task(project, user, task):
    db.session.add(task)


def delete_application(application):
    db.session.delete(application)
    db.session.commit()
    # TODO: remove notification

# projects = db.session.query(Member_Role.project_id).filter(Member_Role.user_id==None, Member_Role.role==role2)
# p = db.session.query(Project).filter(Project.id.in_(projects), Project.estimated_time>=11)
# for x in p:
#     print(x.name)
