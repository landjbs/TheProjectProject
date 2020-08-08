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
