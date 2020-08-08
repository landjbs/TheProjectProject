from flask import flash

from app import db
from app.models import (Project, User, Subject, User_Subjects,
                        User_Report, Notification)


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
    db.session.close()



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
    db.session.close()
    return True


def delete_project(project):
    for member in project.members:
        for subject in project.subjects:
            remove_subject_from_user(member, subject)
    db.session.delete(project)
    db.session.commit()
    db.session.close()
    return True


def create_project(project, user=None, batch=False):
    if not user:
        user = project.owner
    # add project subjects to user
    for subject in project.subjects:
        add_subject_to_user(user, subject)
    # add project to user projects
    user.projects.append(project)
    db.session.add(project)
    db.session.commit()
    if not batch:
        db.session.close()


def complete_project(project):
    if not project.complete:
        project.complete = True
        note = Notification(text=f'Congratulations—{project.name} has been marked as complete by the owner!')
        for member in project.members:
            if not member==project.owner:
                member.notifications.append(note)
        flash(f'Congratulations on completing {project.name}!')
        project.update_last_active()
        db.session.commit()
        db.session.close()
        return True
    return False


def uncomplete_project(project):
    if project.complete:
        project.complete = False
        note = Notification(text=f'{project.name} has been marked as incomplete by the owner. You can now post and complete tasks!')
        for member in project.members:
            if not member==project.owner:
                member.notifications.append(note)
        flash(f'You have marked {project.name} as incomplete. We are excited to see where you will take it!')
        db.session.commit()
        db.session.close()
        return True
    return False


def open_project(project):
    if not project.open:
        project.open = True
        note = Notification(text=f'{project.name} has been opened by the owner.')
        for member in project.members:
            if not member==project.owner:
                member.notifications.append(note)
    db.session.commit()
    db.session.close()
    flash(f'You have opened {project.name}.')
    return True


def close_project(project):
    if project.open:
        project.open = False
        note = Notification(text=f'{project.name} has been closed by the owner.')
        for member in project.members:
            if not member==project.owner:
                member.notifications.append(note)
    db.session.commit()
    db.session.close()
    flash(f'You have closed {project.name}.')
    return True


def remove_application_requirement(project):
    if project.requires_application:
        project.requires_application = False
        note = Notification(text=f'The application requirement has been removed from {project.name} by the owner.')
        for member in project.members:
            if not member==project.owner:
                member.notifications.append(note)
    db.session.commit()
    db.session.close()
    flash(f'You have removed the application requirement from {project.name}.')
    return True


def add_application(project, question):
    if not project.requires_application:
        note = Notification(text=f'An application requirement has been added to {project.name} by the owner.')
        for member in project.members:
            if not member==project.owner:
                member.notifications.append(note)
        flash(f'You have added an application requirement to {project.name}.')
    else:
        flash(f'You have edited the application for {project.name}.')
    project.requires_application = True
    project.application_question = question
    db.session.commit()
    db.session.close()
    return True


def add_comment(project, user, comment):
    project.comments.append(comment)
    db.session.add(comment)
    db.session.commit()
    db.session.close()


def add_task(project, user, task):
    project.tasks.append(task)
    project.update_last_active()
    db.session.add(task)
    db.session.commit()
    db.session.close()


def delete_application(application):
    db.session.delete(application)
    db.session.commit()
    db.session.close()
    # TODO: rem notification from project owner
