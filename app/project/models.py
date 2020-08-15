from datetime import datetime
from sqlalchemy.orm import relationship, backref

from app.database import db, CRUDMixin, generate_code
############################# notifications ####################################
from app.notification.models import Notification
################################################################################
############################# questions ########################################
from app.question.models import Question
from app.question.suggest import suggest_questions, choose_init_questions
################################################################################
############################## links ###########################################
from app.link.models import Link
################################################################################

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
    # instructions
    instructions = db.Column(db.Text(3000), nullable=True)
    # links
    links = relationship('Link',
                         back_populates='project',
                         lazy='dynamic',
                         cascade='all, delete, delete-orphan')
    # subject
    subjects = relationship('Subject', secondary='project_to_subject',
                            back_populates='projects', lazy='dynamic')
    # question
    questions = relationship('Question',
                             back_populates='project',
                             cascade='all, delete, delete-orphan',
                             lazy='dynamic',
                             order_by='Question.asked_on')
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
    buzz = db.Column(db.Integer, nullable=False, default=0)
    # comments
    comments = relationship('Comment', back_populates='project', lazy='dynamic')
    # tasks
    tasks = relationship('Task', back_populates='project', lazy='dynamic')
    # notifications
    notifications = relationship('Notification',
                                 back_populates='project',
                                 lazy='dynamic',
                                 cascade='all, delete, delete-orphan',
                                 order_by='desc(Notification.timestamp)')

    def __init__(self, name, oneliner, summary, url, open, subjects,
                requires_application, application_question, estimated_time,
                team_size, complete, owner):
        self.name = str(name)
        self.code = generate_code(name, Project)
        self.oneliner = str(oneliner)
        self.summary = str(summary)
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
        self.add_member(owner, notify_owner=False)
        ### if url, add it to project ###
        if url is not None:
            self.add_link(url=url, public=True)
        ### choose questions and add them to project ###
        for question in choose_init_questions(self):
            self.add_question(question=question)


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
    def is_owner(self, user):
        ''' Checks if user is ownewr of project '''
        return (user==self.owner)

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
                          important=True, project=self)
        self.update()
        user.notify(text=f'You have applied to {self.name}.',
                    project=self)
        return True

    def accept_application(self, user):
        ''' Accpets pending application of user_id to project '''
        # validate that user has applied
        application = self.get_application(user)
        if not application:
            return False
        # add user to project
        self.add_member(user, notify_owner=False)
        return True

    def reject_application(self, user, by_owner:bool):
        ''' Remove application of user to project '''
        # validate that user has applied
        application = self.get_application(user)
        if not application:
            return False
        # remove application
        db.session.delete(application)
        # add rejection to user
        user.add_rejection(self)
        # notify user
        if by_owner:
            user.notify(
                text=(f'The owner of {self.name} decided not '
                       'to add you to the project right now. '
                       "We promise it's nothing personal! "
                       'Please contact us if you think something'
                       ' is wrong or have any questions.'),
                important=True,
                project=self
            )
        else:
            for note in self.owner.notifications:
                if (user.name in note.text) and (self.name in note.text):
                    self.owner.notifications.remove(note)
        self.update()
        return True


    def notify_owner(self, text, important=False):
        ''' Notify owner with text and category '''
        self.owner.notifications.append(
            Notification(
                text=text,
                project=self,
                important=important
            )
        )
        self.update()
        return True

    def notify_members(self, text, important=False, include_owner=True):
        ''' Notify project members with text and category '''
        if include_owner:
            owner = self.owner
        for member in self.members:
            if not include_owner:
                if member==self.owner:
                    continue
            member.notify(text, important=important, project=self)
        return True

    def add_member(self, user, notify_owner):
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
                            include_owner=notify_owner)
        # add member to project
        self.members.append(user)
        # add xp to user
        user.action_xp('join_project')
        # update project data and activity
        self.update_last_active()
        self.update()
        return True

    def remove_member(self, user_id:int, by_owner:bool):
        ''' Removes member from project '''
        # verify that user is a member
        user = self.members.filter_by(id=user_id).first()
        if not user:
            return False
        # remove project subjects from user
        user.remove_subjects(self.subjects)
        # remove user from project
        self.members.remove(user)
        # notifications
        if by_owner:
            self.notify_members(
                text=(f'{user.name} has been removed from {self.name}.'),
                include_owner=False
            )
            user.notify(text=f'You have been removed from '
                             f'{self.name} by the owner. We promise '
                             "it's nothing personal! Please contact us "
                             'if you think something is wrong or have '
                             'any questions.',
                             important=important,
                             project=project)
        else:
            self.notify_members(
                text=(f'{user.name} has been left {self.name}.')
            )
        # remove xp from user
        user.action_xp('join_project', positive=False)
        # add rejection from project to user
        user.add_rejection(self)
        self.update_last_active()
        self.update()
        return True

    def make_owner(self, user):
        ''' Makes user_id owner of the project '''
        if not self.is_member(user):
            return False
        if user==self.owner:
            return False
        # change owners
        self.owner = user
        # notify new owner
        self.notify_owner(
            text=f'You have been promoted to owner of {self.name}!',
        )
        # notify members
        self.notify_members(
            text=f'Ownership of {self.name} has been transferred to {user.name}.',
            include_owner=False
        )
        self.update_last_active()
        self.update()
        return True

    ## tasks ##
    def todo_tasks(self):
        ''' Returns active tasks on project that haven't been completed '''
        return self.tasks.filter_by(complete=False)

    def completed_tasks(self):
        ''' Returns active tasks on project that have been completed '''
        return self.tasks.filter_by(complete=True)

    def add_task(self, text, author):
        ''' Adds task to project from author, checks permissions '''
        if not self.is_member(author):
            return False
        self.tasks.append(Task(text=text, author=author))
        self.update_last_active()
        self.update()
        self.notify_members(text=f'{author.name} added the task, "{text}".')
        return True

    def change_task_status(self, task_id, user, action):
        ''' Changes status of task in project '''
        task = self.tasks.filter_by(id=task_id).first()
        if not task or not self.is_member(user):
            return False
        if action=='complete':
            if not task.complete:
                task.mark_complete(user)
                self.notify_members(text=f'{user.name} completed the task, "{task.text}".')
            else:
                task.add_worker(user)
        elif action=='back':
            task.remove_worker(user)
            if (task.worker_num()==0):
                task.mark_incomplete()
        elif action=='delete':
            if (not task.complete) and (user in [task.author, self.owner]):
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
        self.notify_members(text=f'{author.name} commented "{text}".')
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

    ## questions ##
    def suggest_questions(self):
        ''' Generates list of suggested questions based on project stats '''
        return suggest_questions(self)

    def add_question(self, question, answer=None):
        self.questions.append(Question(question=question, answer=answer))
        self.update()
        return True

    def remove_question(self, question_id):
        question = self.questions.filter_by(id=question_id).first()
        if not question:
            return False
        question.delete()
        return True

    def n_unanswered(self):
        ''' Gets number of unanswered questions '''
        return self.questions.filter_by(answer=None).count()

    ## links ##
    def add_link(self, url, public, category):
        # check if link is already in project (in same place with same category)
        prev = self.links.filter_by(url=url, public=public, category=category).first()
        if prev is None:
            self.links.append(Link(url=url, public=public, category=category))
            self.update()
            return True
        return False

    def remove_link(self, link_id):
        link = self.links.filter_by(id=link_id).first()
        if not link:
            return False
        link.delete()
        return True

    def public_links(self):
        ''' Gets all public links affiliated with project '''
        return self.links.filter_by(public=True)

    def private_links(self):
        ''' Gets all public links affiliated with project '''
        return self.links.filter_by(public=False)

    def get_other_private_links(self):
        ''' Gets all private links of category other '''
        return self.links.filter_by(public=False, category=0)

    def get_link_category(self, category):
        ''' Gets private link of category '''
        return self.links.filter_by(category=int(category)).first()

    ## status ##
    def mark_complete(self):
        ''' Mark project as complete '''
        if not self.complete:
            self.complete = True
            self.notify_members(
                text=(f'Congratulations—{self.name} has been marked as '
                       'complete by the owner!'),
                important=True,
                include_owner=False
            )
            self.update_last_active()
            self.update()
            return True
        return False

    def mark_incomplete(self):
        ''' Mark project as incomplete '''
        if self.complete:
            self.complete = False
            self.estimated_time = (datetime.utcnow() - self.posted_on).days
            self.notify_members(
                text=(f'{self.name} has been marked as incomplete by the '
                       'owner. You can now post and complete tasks!'),
                important=True,
                include_owner=False
            )
            self.update()
            return True
        return False

    def mark_closed(self):
        ''' Mark project as closed '''
        if self.open:
            self.open = False
            self.notify_members(
                    text=f'{self.name} has been closed by the owner.',
                    include_owner=False)
            self.update_last_active()
            self.update()
            return True
        return False

    def mark_open(self):
        ''' Mark project as open '''
        if not self.open:
            self.open = True
            self.notify_members(
                    text=f'{self.name} has been opened by the owner.',
                    include_owner=False)
            self.update_last_active()
            self.update()
            return True
        return False

    def add_application(self, question:str):
        ''' Turns on application requirement with question '''
        self.requires_application = True
        self.application_question = question
        self.update_last_active()
        self.update()
        return True

    def remove_application(self):
        ''' Turns off application requirement and accepts all pending members '''
        self.requires_application = False
        for application in self.pending:
            self.add_member(application.user, notify_owner=False)
        self.notify_members(text=(f'The application requirement has been '
                                  f'removed from {self.name} by the owner.'),
                            include_owner=False)
        self.update_last_active()
        self.update()
        return True

    def n_applications(self):
        return self.pending.count()

    ## xp and badges ##
    def action_xp_all_members(self, action:str, positive:bool=True):
        for member in self.members:
            member.action_xp(action, positive)
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
    apply_stamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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

    def delete(self, commit=True):
        # remove xp from members
        self.author.action_xp('add_task', positive=False)
        for worker in self.workers:
            worker.action_xp('complete_task', positive=False)
        db.session.delete(self)
        return commit and db.session.commit()

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
            # add xp
            worker.action_xp('complete_task')
            # add to task
            self.workers.append(worker)
            self.update()
            return True
        return False

    def remove_worker(self, worker):
        ''' Removes worker from task '''
        if worker in self.workers:
            # add xp
            worker.action_xp('complete_task', positive=False)
            # remove from task
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
