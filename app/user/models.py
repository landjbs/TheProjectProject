from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import relationship

from app.database import db, CRUDMixin, generate_code
from app.extensions import bcrypt

from app.subject.models import User_Subjects
from app.notification.models import Notification
# from app.message.models import User_Channel, Channel
from app.badge.models import Badge, User_Badge
from app.badge.create_badges import badge_name_list

from .xp_constants import xp_constants


class User(CRUDMixin, UserMixin, db.Model): # SearchableMixin
    __tablename__ = 'user'
    # __searchable__ = ['name', 'about']
    # name
    name = db.Column(db.String(128), nullable=False, unique=False)
    # code
    code = db.Column(db.String(128), nullable=False, unique=True)
    # email
    email = db.Column(db.String(254), unique=True, nullable=False)
    # password
    password = db.Column(db.String(254), nullable=False)
    # subject
    subjects = relationship('Subject', secondary='user_to_subject',
                            back_populates='users', lazy='dynamic')
    # about
    about = db.Column(db.String(500), nullable=False)
    ## permissions and other bools ##
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    applied_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    accepted_on = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=False)
    last_active = db.Column(db.DateTime, nullable=True)
    available = db.Column(db.Boolean, nullable=True, default=True)
    ## projects ##
    owned = relationship('Project',
                        back_populates='owner',
                        lazy='dynamic',
                        order_by='desc(Project.last_active)')
    projects = relationship('Project',
                            secondary='user_to_project_2',
                            back_populates='members',
                            lazy='dynamic',
                            order_by='desc(Project.last_active)')
    pending = relationship('Project_Application',
                            back_populates='user',
                            lazy='dynamic',
                            order_by='desc(Project_Application.apply_stamp)')
    invitations = relationship('Project',
                            secondary='project_invitation',
                            back_populates='invitations',
                            lazy='dynamic',
                            order_by='desc(Project.last_active)')
    rejections = relationship('Project',
                            secondary='project_rejections',
                            lazy='dynamic',
                            back_populates='rejections')
    ## interactions ##
    # channels
    channels = relationship('User_Channel',
                            lazy='dynamic',
                            cascade='all, delete, delete-orphan',
                            back_populates='user',
                            order_by='desc(User_Channel.last_read)')
    # messages
    messages = relationship('Message',
                        back_populates='sender',
                        lazy='dynamic',
                        cascade='all, delete, delete-orphan',
                        order_by='desc(Message.timestamp)')
    # starred projects
    starred = relationship('Project',
                        secondary='user_to_project',
                        back_populates='stars')
    # comments
    comments = relationship('Comment',
                            back_populates='author',
                            cascade='all, delete, delete-orphan')
    tasks_authored = relationship('Task', back_populates='author')
    tasks_worked = relationship('Task',
                                secondary='user_to_task',
                                back_populates='workers',
                                order_by='desc(Task.complete_stamp)')
    # notifications
    notifications = relationship('Notification',
                                 back_populates='user',
                                 lazy='dynamic',
                                 cascade='all, delete, delete-orphan',
                                 order_by='desc(Notification.timestamp)')
    ## honors ##
    # badges
    badges = relationship('User_Badge',
                          back_populates='user',
                          lazy='dynamic',
                          cascade='all, delete, delete-orphan',
                          order_by='desc(User_Badge.last_active)')
    # subjects
    subjects = relationship('User_Subjects',
                            back_populates='user',
                            lazy='dynamic',
                            cascade='all, delete, delete-orphan',
                            order_by='desc(User_Subjects.number)')
    # xp
    xp = db.Column(db.Integer, nullable=False, default=0)
    ## company ##
    companies = relationship(
        'Company',
        secondary='user_to_company',
        back_populates='members'
    )
    ## reporting ##
    # reports targeting user
    reports = relationship('User_Report',
                           back_populates='reported',
                           primaryjoin='User.id==User_Report.reported_id',
                           lazy='dynamic',
                           cascade='all, delete, delete-orphan')

    def __init__(self, name, email, password, about, accepted=False, admin=False):
        self.name = str(name)
        self.code = generate_code(name, User)
        self.email = str(email)
        self.set_password(password)
        self.about = str(about)
        self.admin = admin
        self.accepted = True if admin else False
        self.accepted = accepted if not admin else True
        self.confirmed = True if admin or accepted else False

    def __repr__(self):
        return f'<User {self.name}>'

    def get_url(self):
        return f'/user={self.code}'

    # auth/login
    def get_id(self):
        return str(self.id)

    def is_active(self):
        return self.active

    def recently_active(self, second_window=302400):
        ''' second_window: number of seconds to count as recent.
            currently half a week.
            (week=604800), ()
        '''
        if self.active:
            return True
        if not self.last_active:
            return False
        diff = (datetime.utcnow() - self.last_active).seconds
        if diff>second_window:
            return False
        return True

    def is_authenticated(self):
        return self.accepted

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.admin

    def accept(self):
        if not self.confirmed:
            raise RuntimeError(f'{self} email has not been confirmed.')
        elif self.accepted:
            raise RuntimeError(f'{self} has already been accepted.')
        self.accepted = True
        self.accepted_on = datetime.utcnow()
        self.available = True
        self.update()
        return True

    def reject(self):
        self.accepted = False
        self.accepted_on = None
        self.update()
        return True

    def update_last_active(self):
        self.last_active = datetime.utcnow()
        self.update()
        return True

    # password
    def set_password(self, password):
        hash_ = bcrypt.generate_password_hash(password, 10).decode('utf-8')
        self.password = hash_
        return True

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    ## availability ##
    def mark_available(self):
        if not self.available:
            self.available = True
            self.update()
            return True
        return False

    def mark_unavailable(self):
        if self.available:
            self.available = False
            self.update()
            return True
        return False


    ## subjects ##
    def add_subjects(self, subjects, user_selected=False):
        ''' Adds subjects to user subjects '''
        for subject in subjects:
            prev = self.subjects.filter_by(subject=subject).first()
            if prev is not None:
                prev.number += 1
                if user_selected and not prev.user_selected:
                    prev.user_selected = True
            else:
                new = User_Subjects(
                    user=self, subject=subject, user_selected=user_selected
                )
                self.subjects.append(new)
        self.update()
        return True

    def remove_subjects(self, subjects, user_selected=False):
        for subject in subjects:
            prev = self.subjects.filter_by(subject=subject).first()
            if prev:
                new_number = (prev.number - 1)
                if (new_number < 1):
                    db.session.delete(prev)
                else:
                    prev.number = new_number
                    if user_selected and prev.user_selected:
                        prev.user_selected = False
            else:
                return False
        self.update()
        return True

    def change_subjects(self, subjects):
        edits_made = False
        prev_selected = set([s.subject for s in self.selected_subjects()])
        new_subjects = set(subjects)
        to_add = [subject for subject in new_subjects
                    if not subject in prev_selected]
        to_rem = [subject for subject in prev_selected
                    if not subject in new_subjects]
        if len(to_add)>0:
            self.add_subjects(to_add, user_selected=True)
            edits_made = True
        if len(to_rem)>0:
            self.remove_subjects(to_rem, user_selected=True)
            edits_made = True
        return edits_made

    def selected_subjects(self):
        ''' Gets all subjects explicitly selected by user '''
        user_selected = self.subjects.filter_by(user_selected=True)
        return user_selected

    ## messages ##
    def new_messages(self, return_messages):
        ''' Count and return all new messages for user across channels '''
        # data can either be list of messages or inc of message num
        data = ([] if return_messages else 0)
        for uc in self.channels:
            data += uc.channel.unseen(self, return_messages=return_messages)
        return data

    def ordered_channels(self):
        ''' Returns all channels of user with messages ordered by last active '''
        if (self.channels.count() == 0):
            return []
        channels = [
            uc.channel for uc in self.channels if uc.channel.messages.count()>0
        ]
        return sorted(channels, key=(lambda c : c.last_active), reverse=True)

    ## notifications ##
    def notify(self, text, name, important=False, redirect=None):
        ''' Notify user with text and category '''
        note = Notification(text=text, name=name, important=important,
                            redirect=redirect)
        self.notifications.append(note)
        self.update()
        return True

    def notifications_to_show(self):
        ''' Gets important notifications to show user '''
        toshow = list(self.notifications.filter_by(seen=False, important=True))
        for note in toshow:
            note.mark_seen()
        return toshow

    @classmethod
    def notify_all(cls, text, name, important=False, redirect=None):
        ''' Notifies all users '''
        note = Notification(text=text, important=important, redirect=redirect)
        for user in cls.query.all():
            user.notify(text=text,
                        name=name,
                        important=important,
                        redirect=redirect)
        return True

    def n_unseen(self):
        return self.notifications.filter_by(seen=False).count()

    ## starring ##
    def star_project(self, project):
        if not self.has_starred(project):
            self.starred.append(project)
            project.buzz += 1
            self.action_xp('star_project')
            project.action_xp_all_members('earn_star')
            self.update()

    def unstar_project(self, project):
        if self.has_starred(project):
            self.starred.remove(project)
            project.buzz -= 1
            self.action_xp('star_project', positive=False)
            project.action_xp_all_members('earn_star', positive=False)
            self.update()

    def has_starred(self, project):
        return (project in self.starred)

    ## applications ##
    def has_applied(self, project):
        return ((self.pending.filter_by(project=project).first()) is not None)

    ## invitations ##
    def collaborate(self, project, current_user):
        ''' Invites user to collaborate on project if not already affiliated '''
        if not current_user==project.owner:
            return ('Cannot invite collaborator to project you do not own.',
                    'error')
        elif current_user==self:
            return ("You don't need to send an invitation to collaborate with "
                    "yourself!", 'error')
        elif self in project.members:
            return (f'{self.name} is already a member of {project.name}.',
                    'error')
        elif self.has_applied(project):
            return (f'{self.name} has already applied to {project.name}! '
                    'Go to the project page to accept their application.',
                    'error')
        elif self in project.invitations:
            return (f'You have already invited {target_user.name} to join '
                    f'{project.name}. You will be notified when they respond.',
                    'error')
        # notify user
        self.notify(text=(f'{current_user.name} has invited you '
                          f'to collaborate on {project.name}! '
                           'Click here to reply.'),
                    name=project.name,
                    important=True,
                    redirect=project.get_url()
        )
        # delete rejection if it exists
        if project in self.rejections:
            self.rejections.remove(project)
        # add invitation
        self.invitations.append(project)
        # add xp to inviter and invitee
        self.action_xp('recieve_collab')
        current_user.action_xp('send_collab')
        # update project activity
        project.update_last_active()
        self.update()
        message = (f'You have sent {self.name} an invitation to collaborate '
                   f'on {project.name}. You will be notified when they respond.')
        return (message, 'success')

    def reject_collaboration(self, project):
        if not self in project.invitations:
            message = (f'Cannot withdraw invitation, as {self.name} has never '
                       f'been invited to {project.name}.')
            return (message, 'error')
        self.invitations.remove(project)
        self.add_rejection(project)
        self.update()
        message = f'You have rejected the offer to collaborate on {project.name}.'
        project.notify_owner(text=(f'{self.name} has declined your offer to '
                                f'collaborate on {project.name}. We promise '
                                "it's nothing personal. Please contact us if "
                                'you have any questions.'))
        return (message, 'success')


    def withdraw_collaboration(self, project):
        if not self in project.invitations:
            message = (f'Cannot withdraw invitation, as {self.name} has never '
                       f'been invited to {project.name}.')
            return (message, 'error')
        self.invitations.remove(project)
        self.add_rejection(project)
        self.notify(
            text=(f'The owner of {project.name} has withdrawn the invitation '
                "to collaborate. We promise it's nothing personal!"),
            name=project.name
        )
        self.update()
        message = ('You have withdrawn the offer to collaborate on '
                   f'{project.name} with {self.name}.')
        return (message, 'success')

    ## rejections ##
    def add_rejection(self, project):
        self.rejections.append(project)
        self.update()
        return True

    ## badges and xp ##
    def action_xp(self, action:str, positive:bool=True):
        if positive:
            self.xp += xp_constants.action_xp(action)
        else:
            self.xp -= xp_constants.action_xp(action)
        if self.xp<0:
            self.xp = 0
        self.update()
        return True

    def xp_progressbar_width(self):
        ''' Gets width of xp progressbar on user page as css style '''
        return f'width: {100*float(self.xp/xp_constants.verified_xp)}%;'

    def get_user_badge(self, badge):
        ''' Gets user badge assoc for badge '''
        return self.badges.filter_by(badge=badge).first()

    def update_badge(self, badge_name:str):
        ''' Updates badge, adding user_badge or updating progress as necessary '''
        badge = Badge.get_by_name(badge_name)
        if not badge:
            raise ValueError(f'Could not locate badge "{badge_name}".')
        user_badge = self.get_user_badge(badge)
        progress = getattr(self, badge.evaluator)()
        # if user merits start of badge or has already started
        if (progress>0):
            if not user_badge:
                self.notify(
                    text=f'You have started progress on the {badge_name} badge!',
                    name=badge_name,
                    redirect='/perks'
                )
                user_badge = User_Badge(badge)
                self.badges.append(user_badge)
            user_badge.update_progress()
        elif (user_badge is not None):
            user_badge.delete()
        return True

    def update_badges(self, badge_list:list=badge_name_list):
        ''' Performs update_badge on list of badge_names '''
        for badge_name in badge_list:
            self.update_badge(badge_name)
        return True

    def check_name_return_badge(self, badge_name:str):
        ''' choose_badge helper to see if user has badge '''
        badge = Badge.get_by_name(badge_name)
        if badge:
            user_badge = self.get_user_badge(badge)
            if user_badge and user_badge.earned:
                return badge
        else:
            raise ValueError(f'Invalid badge name "{badge_name}".')

    def choose_badge_from_ordered_list(self, badge_list):
        ''' Helper for choose badge, chooses first available badge in list '''
        for badge_name in badge_list:
            badge = self.check_name_return_badge(badge_name)
            if badge:
                return badge
        return None

    def choose_badge(self, card_type:str):
        ''' Chooses best badge to display based on card type '''
        if self.badges.count()<1:
            return None
        # first is always verified
        verified = self.check_name_return_badge('Verified')
        if verified:
            return verified
        # otherwise go through ordered list of possible badges
        if card_type=='project':
            return self.choose_badge_from_ordered_list(
                ['SuperOwner', 'StarStruck', 'SetEmUp', 'WellConnected',
                'Specialist', 'WellStudied', 'KnockEmDown']
            )
        elif card_type=='member':
            return self.choose_badge_from_ordered_list(
                ['SuperMember', 'KnockEmDown', 'WellStudied', 'WellConnected',
                'Specialist', 'StarStruck', 'SetEmUp']
            )
        elif card_type=='search':
            return self.choose_badge_from_ordered_list(
                ['StarStruck', 'Specialist', 'WellStudied', 'SuperOwner',
                'SuperMember', 'KnockEmDown', 'SetEmUp', 'WellConnected']
            )
        else:
            raise ValueError(f'choose_badge got invalid card_type {card_type}.')

    ## badge allocation evaluators ##
    def n_owned_complete(self):
        ''' Number of owned projects user has completed '''
        n = self.owned.filter_by(complete=True).count()
        return n

    def n_member_complete(self):
        ''' Number of member projects user has completed '''
        completed_projects = self.projects.filter_by(complete=True).count()
        return (completed_projects-self.n_owned_complete())

    def total_skill_level(self):
        ''' Get cumulative skill level of user '''
        skill = 0
        for user_subject in self.subjects:
            skill += user_subject.number
        return skill

    def max_skill_level(self):
        ''' Get skill level of top subject for user '''
        skills = [user_subject.number for user_subject in self.subjects]
        return max(skills) if (len(skills)>0) else 0

    def n_unique_members(self):
        ''' Get number of unique users user has worked with '''
        members = set()
        for project in self.projects:
            for member in project.members:
                if not member==self:
                    members.add(member)
        return len(members)

    def n_tasks_authored(self):
        ''' Get number of task authored by user '''
        n = 0
        for _ in self.tasks_authored:
            n += 1
        return n

    def n_tasks_worked(self):
        ''' Get number of tasks worked by user '''
        n = 0
        for _ in self.tasks_worked:
            n += 1
        return n

    def get_xp(self):
        ''' Wraps xp property for badge allocation '''
        return self.xp

    ## public analytics ##
    def n_owned(self):
        ''' Number of projects owned by user '''
        return self.owned.count()

    def n_applied(self):
        ''' Number of projects to which user has applied '''
        return self.pending.count()

    def n_member(self):
        ''' Number of nonowned projects of which user is member '''
        return (self.projects.count()-self.owned.count())

    def total_stars(self):
        ''' Gets total stars earned by user '''
        stars = 0
        for project in self.projects:
            stars += project.stars.count()
        return stars

    def subject_data(self, n=10):
        ''' Gets dict mapping subject name to skill level for n top subjects '''
        return {s.subject.name : s.number for s in self.subjects[:n]}

    def task_data(self):
        ''' Gets dict '''
        raise RuntimeError('Not yet implemented')

    ## reporting
    def report(self, text, reporter):
        self.reports.append(
            User_Report(reporter=reporter, text=text)
        )
        self.update()
        return True


class Anonymous(AnonymousUserMixin):
    ''' Anonymous user '''
    def __init__(self):
        super(Anonymous, self).__init__()

    def is_admin(self):
        return False

    def has_starred(self, project):
        return False

    def has_applied(self, project):
        return False


class User_Report(db.Model):
    __tablename__ = 'user_report'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey(User.id))
    reported_id = db.Column(db.Integer, db.ForeignKey(User.id))
    reporter = relationship('User', foreign_keys='User_Report.reporter_id')
    reported = relationship('User', foreign_keys='User_Report.reported_id')
    ## description ##
    # report description
    text = db.Column('text', db.String(250), nullable=True)
    # report time
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ## administrative ##
    # has report been addressed
    resolved = db.Column(db.Boolean, nullable=False, default=False)
    # action: what action was taken {0:pass, 1:warning, 2:tempban, 3:permaban}
    action = db.Column(db.Integer, nullable=True)
    # resolve_stamp: when action was taken
    resolve_stamp = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        base = (f'<Report of {self.reported} by {self.reporter} at {self.timestamp}; '
                f'TEXT={self.text}')
        if not self.resolved:
            return (base + f'resolved with {self.action} at {self.resolve_stamp}>')
        else:
            return base + '>'

    def resolve(action):
        ''' action = {0:pass, 1:warning, 2:tempban, 3:permaban} '''
        self.resolved = True
        self.action = int(action)
        self.resolve_stamp = datetime.utcnow()
