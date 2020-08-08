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
