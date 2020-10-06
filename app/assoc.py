'''
Association tables for linking models.
'''

from app.database import db


## ASSOCIATION db.TableS ##
user_to_subject = db.Table('user_to_subject', db.Model.metadata,
              db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
              db.Column('subject_id', db.Integer, db.ForeignKey('subject.id')))


project_to_subject = db.Table('project_to_subject', db.Model.metadata,
            db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
            db.Column('subject_id', db.Integer, db.ForeignKey('subject.id')))


user_to_project = db.Table('user_to_project', db.Model.metadata,
            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('project_id', db.Integer, db.ForeignKey('project.id')))


user_to_project_2 = db.Table('user_to_project_2', db.Model.metadata,
            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('project_id', db.Integer, db.ForeignKey('project.id')))


user_to_task = db.Table('user_to_task', db.Model.metadata,
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('task_id', db.Integer, db.ForeignKey('task.id')))


# stores users and notifcations they have recieved
user_to_notification = db.Table('user_to_notification', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('notification_id', db.Integer, db.ForeignKey('notification.id')))


# stores invitations of users to join projects
project_invitation = db.Table('project_invitation', db.Model.metadata,
            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('project_id', db.Integer, db.ForeignKey('project.id')))


# stores users/projects rejected from each other
project_rejections = db.Table('project_rejections', db.Model.metadata,
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('project_id', db.Integer, db.ForeignKey('project.id')))


# badge to perks
badge_to_perk = db.Table('badge_to_perk', db.Model.metadata,
            db.Column('badge_id', db.Integer, db.ForeignKey('badge.id')),
            db.Column('perk_id', db.Integer, db.ForeignKey('badge_perk.id')))


# # company to project
# company_to_project = db.Table('company_to_project', db.Model.metadata,
#             db.Column('company_id', db.Integer, db.ForeignKey('company.id')),
#             db.Column('project_id', db.Integer, db.ForeignKey('project.id')))
#
#
# # company to user
user_to_company = db.Table('user_to_company', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id')))
