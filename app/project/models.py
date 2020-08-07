from datetime import datetime
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin, generate_code
from app.notification.models import Notification


class Project(CRUDMixin, db.Model):
    __tablename__ = 'project'
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    ## base info ##
    # name
    name = db.Column(db.String(25), unique=False, nullable=False)
    # code for url
    code = db.Column(db.String(128), unique=True, nullable=False)
    # oneliner
    oneliner = db.Column(db.String(40))
    # summary
    summary = db.Column(db.String(400), nullable=False)
    # url
    url = db.Column(db.String(128), nullable=True)
    # subject
    subjects = relationship('Subject', secondary='project_to_subject',
                            back_populates='projects', lazy='dynamic')
    ## people ##
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = relationship('User', back_populates='owned')
    members = relationship('User', secondary='user_to_project_2',
                           back_populates='projects', lazy='dynamic')
    pending = relationship('Project_Application',
                            back_populates='project', lazy='dynamic')
    invitations = relationship('User', secondary='project_invitation',
                               back_populates='invitations', lazy='dynamic')
    rejections = relationship('User', secondary='project_rejections',
                              back_populates='rejections')
    ## join process ##
    # open (allows others to join)
    open = db.Column(db.Boolean, nullable=False)
    # requires application
    requires_application = db.Column(db.Boolean, nullable=False)
    # applicaiton question
    application_question = db.Column(db.String(128), nullable=True)
    # max team size
    team_size = db.Column(db.Integer, nullable=False)
    ## timing ##
    # posted_on
    posted_on = db.Column(db.DateTime, nullable=False)
    # complete_on
    completed_on = db.Column(db.DateTime, nullable=True)
    # last activity
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # estimated time
    estimated_time = db.Column(db.Integer, nullable=True)
    # complete
    complete = db.Column(db.Boolean, nullable=False)
    ## popularity ##
    # stars
    stars = relationship('User', secondary='user_to_project',
                         back_populates='starred', lazy='dynamic')
    # buzz
    buzz = db.Column(db.Integer, nullable=False)
    # comments
    comments = relationship('Comment', back_populates='project', lazy='dynamic')
    # tasks
    tasks = relationship('Task', back_populates='project', lazy='dynamic')

    def __init__(self, name, oneliner, summary, url, open, subjects,
                requires_application, application_question, estimated_time,
                team_size, complete, owner):
        self.name = str(name)
        self.code = generate_code(name, Project)
        self.oneliner = str(oneliner)
        self.summary = str(summary)
        self.url = str(url) if url else None
        self.subjects = subjects
        # members
        self.owner = owner
        self.team_size = team_size
        # application
        self.open = bool(open)
        self.requires_application = bool(requires_application)
        self.application_question = str(application_question) if requires_application else None
        # timing and completion
        cur_time = datetime.utcnow()
        self.posted_on = cur_time
        self.completed_on = cur_time if complete else None
        self.estimated_time = estimated_time if not complete else None
        self.complete = bool(complete)
        self.buzz = 0

    def __repr__(self):
        return f'<Project {self.name}>'

    ## activity ##
    def recently_active(self, second_window=302400):
        ''' second_window: number of seconds to count as recent.
            currently half a week.
            (week=604800), ()
        '''
        if not self.last_active:
            return False
        diff = (datetime.utcnow() - self.last_active).seconds
        if diff>second_window:
            return False
        return True

    def update_last_active(self):
        self.last_active = datetime.utcnow()

    ## members ##
    def is_member(self, user):
        ''' Checks if user is a member of project '''
        return (user in self.members)

    def get_application(self, user):
        ''' Gets application of user to project if exists else returns None '''
        return self.pending.filter_by(user=user).first()

    def apply(self, user, text):
        self.pending.append(
            Project_Application(
                user=user,
                text=text
            )
        )
        self.notify_owner(text=f'{user.name} has applied to {self.name}!',
                             category=0)
        self.update()

    def notify_owner(self, text, category=0):
        ''' Notify owner with text and category '''
        self.owner.notifications.append(
            Notification(
                text=text,
                category=category
            )
        )
        self.update()

    def notify_members(self, text, category, include_owner=True):
        ''' Notify project members with text and category '''
        notification = Notification(text=text, category=category)
        if include_owner:
            owner = self.owner
        for member in self.members:
            if not include_owner:
                if member==self.owner:
                    continue
            member.add_notification(notification)

    def add_member(self, user):
        ''' Adds member to project '''
        # add project subjects to user
        user.add_subjects(self.subjects)
        # delete user application if it exists
        application = self.pending.filter_by(user=user).first()
        if application is not None:
            db.session.delete(application)
        # delete user invitation if it exists
        if user in self.invitations:
            self.invitations.remove(user)
        # delete user rejection if it exists
        if user in self.rejections:
            self.rejections.remove(user)
        # notify other project members
        self.notify_members(text=f'{user.name} has joined {self.name}.',
                            category=0)
        # add member to project
        self.members.append(user)
        # update project data and activity
        self.update_last_active()
        self.update()
        return True

    def remove_member(self, user_id, by_owner):
        ''' Removes member from project '''


    def change_user_status(self, user, action):
        if action=='accept':
            if not user in self.members:
                return False
            self.add_member(user)
        elif action=='reject':


    ## tasks ##
    def todo(self):
        ''' Returns active tasks on project that haven't been completed '''
        return self.tasks.filter_by(complete=False)

    def completed(self):
        ''' Returns active tasks on project that have been completed '''
        return self.tasks.filter_by(complete=True)

    def add_task(self, text, author):
        ''' Adds task to project from author, checks permissions '''
        if not self.is_member(author):
            return False
        self.tasks.append(Task(text=text, author=author))
        self.update_last_active()
        self.update()
        return True

    def change_task_status(self, task_id, user, action):
        ''' Changes status of task in project '''
        task = self.tasks.filter_by(id=task_id).first()
        if not task or not self.is_member(user):
            return False
        if action=='complete':
            if not task.complete:
                task.mark_complete(user)
            else:
                task.add_worker(user)
        elif action=='back':
            task.remove_worker(user)
            if (task.worker_num()==0):
                task.mark_incomplete()
        elif action=='delete':
            if user==task.author:
                task.delete()
        else:
            raise ValueError(f'Invalid action {action} for change_task_status.')
        self.update_last_active()
        return True

    ## comments ##
    def add_comment(self, text, author):
        ''' Adds comment to project '''
        self.comments.append(Comment(text=text, author=author))
        self.update()
        return True

    def delete_comment(self, comment_id, user):
        ''' Deletes comment from project '''
        comment = self.comments.filter_by(id=comment_id).first()
        if not comment or not user in [self.owner, comment.author]:
            return False
        self.comments.remove(comment)
        comment.delete()
        self.update()
        return True

    ## public analytics ##
    def subject_data(self):
        ''' Get dict mapping project subject names to member skill levels '''
        project_subjects = {s.name:0 for s in self.subjects}
        if project_subjects!={}:
            for member in self.members:
                for user_subject in member.subjects:
                    name = user_subject.subject.name
                    if name in project_subjects:
                        # -1 to account for skills gained via project association
                        project_subjects[name] += (user_subject.number)
        return project_subjects

    def task_number(self):
        # TODO: make efficient
        n = 0
        for task in self.tasks:
            n += 1
        return n


class Project_Application(db.Model):
    __tablename__ = 'project_application'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = relationship('User', back_populates='pending')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    project = relationship('Project', back_populates='pending')
    text = db.Column('text', db.String(250), nullable=True)

    def __repr__(self):
        return f'<Application of {self.user.name} to {self.project.name}; Text={self.text}>'


class Task(CRUDMixin, db.Model):
    __tablename__ = 'task'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # text
    text = db.Column(db.String(160), nullable=True)
    # author
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    author = relationship('User', back_populates='tasks_authored')
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', back_populates='tasks')
    # workers
    workers = relationship('User', secondary='user_to_task',
                           back_populates='tasks_worked')
    # timing
    post_stamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    complete_stamp = db.Column(db.DateTime, nullable=True)
    complete = db.Column(db.Boolean, default=False)

    def mark_complete(self, worker):
        ''' Marks incomplete task as complete '''
        if not self.complete:
            self.add_worker(worker)
            self.complete = True
            self.complete_stamp = datetime.utcnow()
            self.update()
            return True
        return False

    def mark_incomplete(self):
        ''' Marks completed task as incomplete '''
        if self.complete:
            self.complete = False
            self.complete_stamp = None
            self.update()
            return True
        return False

    def add_worker(self, worker):
        ''' Adds worker to task '''
        if not worker in self.workers:
            self.workers.append(worker)
            self.update()
            return True
        return False

    def remove_worker(self, worker):
        ''' Removes worker from task '''
        if worker in self.workers:
            self.workers.remove(worker)
            self.update()
            return True
        return False

    ## public analytics ##
    def worker_num(self):
        ''' Gets number of workers on task '''
        return len(self.workers)


class Comment(CRUDMixin, db.Model):
    __tablename__ = 'comment'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # text
    text = db.Column(db.String(160), nullable=False)
    # author
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship('User', back_populates='comments')
    # project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = relationship('Project', back_populates='comments')
    # time
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Comment {self.author.name} on {self.project.name} at {self.timestamp}; TEXT={self.text}>'
