from datetime import datetime
from heapq import nlargest
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
########################### competitions #######################################
from app.competition.models import Submission
################################################################################


class Project(CRUDMixin, db.Model): # SearchableMixin
    __tablename__ = 'project'
    # __searchable__ = ['name', 'oneliner', 'summary']
    ## base info ##
    # name
    name = db.Column(db.String(25), unique=False, nullable=False)
    # code for url
    code = db.Column(db.String(128), unique=True, nullable=False)
    # oneliner
    oneliner = db.Column(db.String(40), nullable=False)
    # summary
    summary = db.Column(db.String(400), nullable=False)
    # instructions
    instructions = db.Column(db.Text(3000), nullable=True)
    # type {0:indep, 1:startup}
    # type = db.Column(db.Integer, nullable=False, default=0)
    # links
    links = relationship(
        'Link',
        back_populates='project',
        lazy='dynamic',
        cascade='all, delete, delete-orphan'
    )
    # subject
    subjects = relationship(
        'Subject',
        secondary='project_to_subject',
        back_populates='projects',
        lazy='dynamic'
    )
    # question
    questions = relationship(
        'Question',
        back_populates='project',
        cascade='all, delete, delete-orphan',
        lazy='dynamic',
        order_by='desc(Question.asked_on)'
    )
    ## people ##
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = relationship('User', back_populates='owned')
    members = relationship(
        'User',
        secondary='user_to_project_2',
        back_populates='projects',
        lazy='dynamic'
    )
    pending = relationship(
        'Project_Application',
        back_populates='project',
        lazy='dynamic'
    )
    invitations = relationship(
        'User',
        secondary='project_invitation',
        back_populates='invitations',
        lazy='dynamic'
    )
    rejections = relationship(
        'User',
        secondary='project_rejections',
        back_populates='rejections'
    )
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
    stars = relationship(
        'User',
        secondary='user_to_project',
        back_populates='starred',
        lazy='dynamic'
    )
    # buzz
    buzz = db.Column(db.Integer, nullable=False, default=0)
    # company
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    company = relationship(
        'Company',
        secondary='company_to_project',
        back_populates='projects',
        lazy='dynamic'
    )
    # competition
    competition = relationship(
        'Submission',
        uselist=False,
        back_populates='project',
        cascade='all, delete, delete-orphan'
    )
    # comments
    comments = relationship(
        'Comment',
        back_populates='project',
        lazy='dynamic',
        cascade='all, delete, delete-orphan',
        order_by='Comment.timestamp'
    )
    # tasks
    tasks = relationship(
        'Task',
        back_populates='project',
        lazy='dynamic',
        cascade='all, delete, delete-orphan',
        order_by='desc(Task.complete_stamp)'
    )

    def __init__(
        self,
        name,
        oneliner,
        summary,
        open,
        subjects,
        requires_application,
        application_question,
        estimated_time,
        team_size,
        complete,
        owner,
        competition=None
    ):
        self.name = str(name)
        self.code = generate_code(name, Project)
        self.oneliner = str(oneliner)
        self.summary = str(summary)
        self.subjects = subjects
        # members
        self.owner = owner
        self.team_size = team_size if team_size else 1 # TODO: team size should be equal to current team_size
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
        ### if competition, add it to project ##
        if competition:
            self.submit_to_competition(competition)
        ### choose questions and add them to project ###
        for question in choose_init_questions(self):
            self.add_question(question=question, notify=False)

    @classmethod
    def build_from_form(self, form, owner, subjects, competition):
        ''' Builds Project instance from Add_Form '''
        data = form.data
        name                    =       data.get('name')
        oneliner                =       data.get('oneliner')
        summary                 =       data.get('summary')
        subjects                =       subjects
        owner                   =       owner
        # TODO: others
        # others = get_members()
        estimated_time          =       data.get('estimated_time')
        complete                =       data.get('complete')
        open                    =       data.get('looking_for_team')
        team_size               =       data.get('target_team_size')
        requires_application    =       data.get('requires_application')
        application_question    =       data.get('application_question')
        return Project(
            name=name,
            oneliner=oneliner,
            summary=summary,
            subjects=subjects,
            open=open,
            requires_application=requires_application,
            application_question=application_question,
            estimated_time=estimated_time,
            team_size=team_size,
            complete=complete,
            owner=owner,
            competition=competition
        )


    def __repr__(self):
        return f'<Project {self.name}>'

    def get_url(self):
        return f'/project={self.code}'

    ## styling ##
    def border_color(self):
        ''' Sets border color for project card. Is this inefficient? Maybe move to jinja or css? '''
        if self.competition and self.competition.winner:
            return 'gold'
        # false uses css default
        return False

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
        self.update()

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
        if user in self.invitations:
            self.add_member(user, notify_owner=True)
        if user in self.rejections:
            self.rejections.remove(user)
        self.pending.append(
            Project_Application(
                user=user,
                text=text
            )
        )
        self.notify_owner(text=f'{user.name} has applied to {self.name}!',
                          important=True)
        self.update()
        user.notify(text=f'You have applied to {self.name}.',
                    name=self.name,
                    redirect=self.get_url())
        return True

    def accept_application(self, user):
        ''' Accpets pending application of user_id to project '''
        # validate that user has applied
        application = self.get_application(user)
        if not application:
            return False
        # add user to project
        self.add_member(user, notify_owner=False)
        user.notify(
            text=f'You have been accepted to {self.name}',
            name=self.name,
            redirect=self.get_url()
        )
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
                       "We promise it's nothing personal!"),
                name=self.name,
                important=True,
                redirect=self.get_url()
            )
        else:
            for note in self.owner.notifications:
                if (user.name in note.text) and (self.name in note.text):
                    self.owner.notifications.remove(note)
        self.update()
        return True


    def notify_owner(self, text, important=False):
        ''' Notify owner with text and category '''
        self.owner.notify(
            text=text,
            name=self.name,
            important=important,
            redirect=self.get_url()
        )
        self.update()
        return True

    def notify_members(self, text, important=False, exclude=[], include_owner=True):
        ''' Notify project members with text and category '''
        exclude = set(exclude)
        if not include_owner:
            exclude.add(self.owner)
        for member in self.members:
            if not member in exclude:
                member.notify(
                    text=text,
                    name=self.name,
                    important=important,
                    redirect=self.get_url()
                )
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
                text=(f'{user.name} has been removed from {self.name}.')
            )
            user.notify(text=f'You have been removed from '
                             f'{self.name} by the owner. We promise '
                             "it's nothing personal! Please contact us "
                             'if you think something is wrong or have '
                             'any questions.',
                             name=self.name,
                             important=True,
                             redirect=self.get_url()
            )
        else:
            self.notify_members(
                text=f'{user.name} has left {self.name}.'
            )
            user.notify(
                text=f'You have left {self.name}.',
                name=self.name,
                redirect=self.get_url()
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
            important=True
        )
        # notify members
        self.notify_members(
            text=f'Ownership of {self.name} has been transferred to {user.name}.',
            include_owner=False
        )
        self.update_last_active()
        self.update()
        return True

    ## subjects ##
    def change_subjects(self, subjects):
        ''' Changes project subjects to subject list '''
        edits_made = False
        prev_subjects = set(self.subjects)
        new_subjects = set(subjects)
        for subject in new_subjects:
            if not subject in prev_subjects:
                self.subjects.append(subject)
                edits_made = True
        for subject in prev_subjects:
            if not subject in new_subjects:
                self.subjects.remove(subject)
                edits_made = True
        if edits_made:
            self.update()
        return edits_made

    ## tasks ##
    def n_todo(self):
        return self.todo_tasks().count()

    def n_complete(self):
        return self.completed_tasks().count()

    def todo_tasks(self):
        ''' Returns active tasks on project that haven't been completed '''
        return self.tasks.filter_by(complete=False)

    def completed_tasks(self):
        ''' Returns active tasks on project that have been completed '''
        return self.tasks.filter_by(complete=True)

    def add_task(self, text, author, notify=True):
        ''' Adds task to project from author, checks permissions '''
        if not self.is_member(author):
            return False
        # build task object
        task = Task(text=text, author=author)
        # add task to project tasks
        self.tasks.append(task)
        # update project last active (which autocommits task changes)
        self.update_last_active()
        # notify members if prompted
        if notify:
            self.notify_members(
                text=f'{author.name} added the task "{text}" to {self.name}.',
                exclude={author}
            )
        # return task object for json rendering
        return task

    def change_task_status(self, task_id, user, action):
        ''' Changes status of task in project '''
        task = self.tasks.filter_by(id=task_id).first()
        if not task or not self.is_member(user):
            return False
        if action=='complete':
            if not task.complete:
                task.mark_complete(user)
                self.notify_members(
                    text=f'{user.name} completed the task, "{task.text}" for {self.name}.',
                    exclude={user}
                )
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
        return task

    ## comments ##
    def add_comment(self, text, author):
        ''' Adds comment to project '''
        comment = Comment(text=text, author=author)
        self.comments.append(comment)
        self.update()
        self.notify_members(
            text=f'{author.name} commented "{text}" on {self.name}.',
            exclude={author}
        )
        return comment

    def pin_comment(self, comment_id):
        ''' Pins comment to top of project box '''
        comment = self.comments.filter_by(id=comment_id).first()
        if comment is None or (comment.pinned==True):
            return False
        comment.pinned = True
        comment.update()
        return comment

    def unpin_comment(self, comment_id):
        ''' Unpins comment '''
        comment = self.comments.filter_by(id=comment_id).first()
        if comment is None or (comment.pinned==False):
            return False
        comment.pinned = False
        comment.update()
        return comment

    def delete_comment(self, comment_id, user):
        ''' Deletes comment from project '''
        comment = self.comments.filter_by(id=comment_id).first()
        if not comment or not user in [self.owner, comment.author]:
            return False
        self.comments.remove(comment)
        comment.delete()
        self.update()
        return True

    def ordered_comments(self):
        ''' Comments in chronological order with pinned at top '''
        pinned      = list(self.comments.filter_by(pinned=True).all())
        unpinned    = list(self.comments.filter_by(pinned=False).all())
        return (pinned + unpinned)
        # return list(self.comments)

    ## questions ##
    def suggest_questions(self):
        ''' Generates list of suggested questions based on project stats '''
        return suggest_questions(self)

    def add_question(self, question, answer=None, notify=True):
        question = Question(question=question, answer=answer)
        self.questions.append(question)
        if notify:
            self.notify_members(
                text=f'Someone asked a new question on {self.name}!'
            )
        self.update()
        return question

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
    def add_link(self, url, public, category=0):
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
                       'complete!'),
                important=True
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
                text=(f'{self.name} has been marked as incomplete. '
                       'You can now post and complete tasks!'),
                important=True
            )
            self.update()
            return True
        return False

    def mark_closed(self):
        ''' Mark project as closed '''
        if self.open:
            self.open = False
            self.notify_members(
                text=f'{self.name} has been closed.',
            )
            self.update_last_active()
            self.update()
            return True
        return False

    def mark_open(self):
        ''' Mark project as open '''
        if not self.open:
            self.open = True
            self.notify_members(
                text=f'{self.name} has been opened.',
            )
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
        self.update_last_active()
        self.update()
        return True

    def n_applications(self):
        return self.pending.count()

    ## competitions ##
    def submit_to_competition(self, competition):
        # if not
        self.competition = Submission(competition=competition, project=self)
        self.notify_members(
            text=(f'{self.name} has been submitted to the '
                f'competition {competition.name}!')
        )
        self.update()
        return True

    ## xp and badges ##
    def action_xp_all_members(self, action:str, positive:bool=True):
        for member in self.members:
            member.action_xp(action, positive)
        return True

    ## public analytics ##
    def elasped(self):
        return int((datetime.utcnow() - self.posted_on).days)

    def estimated_time_safe(self):
        ''' Max of estimated time and elasped time '''
        # get estimated time of project
        estimated = self.estimated_time
        # get elasped time of project
        elasped = int(self.elasped())
        # update estimated time if elaspsed is greater
        if elasped > estimated:
            self.estimated_time = elasped
            self.update()
        return self.estimated_time

    def subject_data(self, n=10):
        ''' Get dict mapping project subject names to member skill levels '''
        project_subjects = {s.name:0 for s in self.subjects}
        if project_subjects!={}:
            for member in self.members:
                for user_subject in member.subjects:
                    name = user_subject.subject.name
                    if name in project_subjects:
                        # -1 to account for skills gained via project association
                        project_subjects[name] += (user_subject.number)
        top_n = nlargest(n, project_subjects, project_subjects.get)
        project_subjects = {k:v for k,v in project_subjects.items()
                            if k in top_n}
        return project_subjects

    def task_number(self):
        # NOTE: inefficient
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
    # pinned
    pinned = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Comment {self.author.name} on {self.project.name} at {self.timestamp}; TEXT={self.text}>'
