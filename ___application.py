import numpy as np
from sqlalchemy import asc, desc
from sqlalchemy.sql.expression import func
from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import (current_user, login_user, logout_user,
                         login_required, LoginManager)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from dateutil import tz
from collections import Counter
from operator import itemgetter
from itsdangerous import URLSafeTimedSerializer

from app import create_app, db
# from app import db
from app.models import (User, Project, Comment, Task, Subject, User_Report,
                        Project_Application, Notification, Anonymous)
import app.forms as forms
import app.jobs as tasks
from flask_admin import Admin
from flask_admin.menu import MenuLink
from auth import UserView, ReportView, AdminBaseView
import manager as manager
import recommendation as rec

# Elastic Beanstalk initalization
application = create_app()


# initalization
login_manager = LoginManager(app=application)
login_manager.init_app(app=application)
login_manager.login_view = 'login'
login_manager.anonymous_user = Anonymous


@login_manager.user_loader
def user_loader(id):
    return User.query.get_or_404(id)


def is_project_member(user, project):
    if user==None:
        return False
    return (user in project.members)


# TEMP: MAILING HERE FOR NOW
def encode_token(email):
    serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')


def decode_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
    try:
        email = serializer.loads(s=token,
                                salt='email-confirm-salt',
                                max_age=expiration)
        return email
    except Exception as e:
        return False


def generate_url(endpoint, token):
    return url_for(endpoint, token=token, _external=True)


# functions
@application.context_processor
def utility_processor():
    def calc_days_since(now, start):
        return int((now - start).days)
    def calc_days_left(elapsed, estimated_time):
        return int((estimated_time - elapsed))
    def elapsed_style(elapsed, estimated_time):
        return f'width: {100*float(elapsed/estimated_time)}%;'
    def time_to_str(time):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        time = time.replace(tzinfo=from_zone)
        time = time.astimezone(to_zone)
        # time = f"{time.strftime('%B %d, %Y')} at {time.strftime('%I:%M %p')}"
        time = f"{time.strftime('%B %d')}"
        time = time.lstrip("0").replace(" 0", " ")
        return time
    def complete(tasks):
        return tasks.filter_by(complete=True)
    def not_complete(tasks):
        return tasks.filter_by(complete=False)
    def is_project_member_(user, project):
        return is_project_member(user, project)
    def now():
        return datetime.utcnow()
    return dict(calc_days_since=calc_days_since, calc_days_left=calc_days_left,
                elapsed_style=elapsed_style, time_to_str=time_to_str,
                not_complete=not_complete, complete=complete,
                is_project_member=is_project_member_, now=now)


def tasks_to_daily_activity(tasks):
    current_time = datetime.utcnow()
    start_stamps = []
    end_stamps = []
    for task in tasks:
        start_stamps.append(round((current_time-task.post_stamp).days))
        # start_stamps.append((current_time-task.post_stamp).days)
        if task.complete:
            end_stamps.append(round(((current_time-task.complete_stamp).days)))
            # end_stamps.append((current_time-task.complete_stamp).days)
    start_activity = Counter(start_stamps)
    end_activity = Counter(end_stamps)
    earliest = max(start_activity)+1
    for i in range(earliest):
        if i not in start_activity:
            start_activity.update({i:0})
        if i not in end_activity:
            end_activity.update({i:0})
    start_activity = [x[1] for x in sorted(start_activity.items(), key=itemgetter(0), reverse=True)]
    end_activity = [x[1] for x in sorted(end_activity.items(), key=itemgetter(0), reverse=True)]
    # for i in range(start_activity):
    return (start_activity, end_activity, earliest)


# querying
def query_user_by_id(id):
    return db.session.query(User).get(int(id))


def query_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()



@application.route('/confirm/<token>')
def confirm_email(token):
    email = decode_token(token)
    if not email:
        flash('The confirmation link is invalid or expired.')
        return redirect(url_for('index'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account has already been confirmed.')
        if user.accepted:
            return redirect(url_for('login'))
        else:
            return redirect(url_for('index'))
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    db.session.close()
    flash('You have confirmed your account!')
    return redirect(url_for('index'))


def send_password_reset_email(user_email):
    reset_serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
    reset_url = url_for('users.reset_with_token',
                        token=reset_serializer.dumps(user_external=True))
    html = render_template('email/password_reset.html')
    send_email('Reset Your Password for TheProjectProject',
                user_email, html)


@application.route('/reset', methods=['GET', 'POST'])
def reset():
    form = forms.Login(request.form)
    if form.validate_on_submit():
        pass
    return redirect(request.referrer)


## HOME ##
def partition_query(l, n=3):
    try:
        c = l.count()
    except:
        c = len(l)
    for i in range(0, c, n):
        yield l[i:i+n]


@application.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # recommended projects
    recs = rec.recommend_projects(current_user)
    # recs = db.session.query(Project).limit(30)
    recommended_tabs = list(partition_query(recs))
    # top projects
    tops = db.session.query(Project).order_by(desc(Project.buzz)).limit(9)
    top_tabs =  list(partition_query(tops))
    # user projects
    user_projs = rec.user_projects(current_user)
    user_tabs = list(partition_query(user_projs))
    project_application = forms.Project_Application_Form(request.form)
    # notifcations
    if (current_user.notifications.count())>0:
        for notification in current_user.notifications:
            flash(notification.text)
            current_user.notifications.remove(notification)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return render_template('home.html', recommended_tabs=recommended_tabs,
                            top_tabs=top_tabs, user_tabs=user_tabs,
                            user_project_count=len(user_projs),
                            current_user=current_user,
                            project_application=project_application)


@application.route('/add_project', methods=['GET', 'POST'])
@login_required
@limiter.limit('10 per minute')
def add_project():
    form = forms.Add_Project(request.form)
    if request.method=='POST' and form.validate_on_submit():
        # url to none
        if form.url.data=='':
            form.url.data=None
        # special errors
        error_flag = False
        if form.requires_application.data and form.application_question.data=='':
            form.application_question.errors = ['Question cannot be blank.']
            error_flag = True
        # unique errors
        if not (db.session.query(Project).filter_by(name=form.name.data).first() is None):
            form.name.errors = ['A project with this name already exists.']
            error_flag = True
        if not (db.session.query(Project).filter_by(url=form.url.data).first() is None):
            form.url.errors = ['A project with this url already exists.']
            error_flag = True
        if (len(form.subjects.data)>5):
            form.subjects.errors = ['Can only choose up to 5 subjects.']
            error_flag = True
        # team size defaults to 1 if None
        if form.team_size.data is None:
            form.team_size.data = 1
        if not error_flag:
            # subjects
            subjects = [Subject.query.get(int(id)) for id in form.subjects.data]
            with db.session.no_autoflush:
                try:
                    project = Project(name = form.name.data,
                                  oneliner=form.oneliner.data,
                                  summary = form.summary.data,
                                  url = form.url.data,
                                  subjects = subjects,
                                  owner = current_user,
                                  open = form.open.data,
                                  requires_application = form.requires_application.data,
                                  application_question = form.application_question.data,
                                  estimated_time = form.estimated_time.data,
                                  team_size = form.team_size.data,
                                  complete = form.complete.data)
                    project_code = project.code
                    manager.create_project(project, current_user, batch=True)
                except Exception as e:
                    flash("Sorry! An error occured when trying to add your "
                        "project. Please try again later.")
                    db.session.rollback()
                    return render_template('add_project.html', form=form)
                # successful message
                flash(f'Congratulations—your project, {form.name.data}, '
                       'has been added!')
                task_message = True
                if form.complete.data==True:
                    flash(f'As a completed project, {form.name.data} will be '
                        'visible, but not joinable or editable.')
                    task_message = False
                elif form.open.data==False:
                    flash(f'As a closed project, {form.name.data} will be '
                          'visible and editable, but not joinable.')
                elif form.requires_application.data==False:
                     flash(f'As an open project with no application, '
                           f'{form.name.data} will be available for others to '
                           'join at any time.')
                elif form.requires_application.data==True:
                    flash(f'As an open project with an application, '
                          f'{form.name.data} can be joined by users you accept. '
                          'Check back soon to manage applicants.')
                if task_message:
                    flash('Try adding some tasks to show what needs to '
                          'be done on your project and posting some comments '
                          "to tell people what it's all about!")
                else:
                    flash('Post some comments to tell people what your project '
                          'is all about!')
                return project_page(project_code)
    return render_template('add_project.html', form=form)


@application.route('/user=<code>', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def user_page(code):
    user = User.query.filter_by(code=code).first_or_404()
    # worked tasks
    tasks = user.tasks_worked
    task_data = {} if (len(tasks)>0) else None
    if task_data is not None:
        _, end_activity, earliest = tasks_to_daily_activity(tasks)
        task_data['end_activity'] = end_activity
        task_data['earliest'] = earliest
    # owned projects
    owned = user.owned
    owned_tabs = list(partition_query(owned))
    # member projects
    member_projects = [project for project in user.projects
                       if not project in owned]
    member_tabs = list(partition_query(member_projects))
    # sum stars
    stars = 0
    for project in user.projects:
        stars += project.stars.count()
    # subjects
    subject_data = {s.subject.name : s.number for s in user.subjects[:10]}
    ## forms ##
    # application to projects
    project_application = forms.Project_Application_Form(request.form)
    # edit user account
    show_edit_modal = False
    edit_form = forms.Edit_User(request.form) if (current_user==user) else False
    if request.method=='POST':
        if edit_form.validate_on_submit():
            edits_made = False
            # name
            new_name = edit_form.name.data
            if new_name!=user.name:
                user.name = new_name
                edits_made = True
            # email
            # new_email = edit_form.email.data
            # if new_email!=user.email:
            #     user.email = new_email
            #     edits_made = True
            # github
            new_github = edit_form.github.data
            if new_github!=user.github:
                user.github = new_github
                edits_made = True
            # about
            new_about = edit_form.about.data
            if new_about!=user.about:
                user.about = new_about
                edits_made = True
            # new password
            if edit_form.password.data!='':
                if not user.check_password(edit_form.password.data):
                    user.password = user.set_password(edit_form.password.data)
                    edits_made = True
            if edits_made:
                flash('You have successfully edited your acount.')
                db.session.add(user)
                db.session.commit()
                db.session.close()
        else:
            show_edit_modal = True
    return render_template('user.html', user=user, stars=stars,
                            task_data=task_data, subject_data=subject_data,
                            owned_tabs=owned_tabs, member_tabs=member_tabs,
                            project_application=project_application,
                            edit_form=edit_form,
                            show_edit_modal=show_edit_modal)




@application.route('/subject=<subject_name>')
@login_required
def subject(subject_name):
    subject = Subject.query.filter_by(code=subject_name).first_or_404()
    # project tabs
    subject_projects = Project.query.filter(Project.subjects.contains(subject)).limit(30)
    project_tabs = list(partition_query(subject_projects))
    # users
    subject_users = [s.user for s in subject.users[:30]]
    user_tabs = partition_query(subject_users)
    #
    subject_tabs = []
    # application
    project_application = forms.Project_Application_Form(request.form)
    return render_template('search.html', project_tabs=project_tabs,
                        user_tabs=user_tabs, subject_tabs=subject_tabs,
                        search_text=subject.name,
                        project_application=project_application)





@application.route('/leave_project/<int:project_id>', methods=['POST'])
@login_required
def leave_project(project_id):
    project = Project.query.get_or_404(project_id)
    # validate that user is member
    if not current_user in project.members:
        flash(f'Cannot leave {project.name} without being a member.')
        return redirect(request.referrer)
    # transfer ownership
    if (current_user==project.owner):
        if (project.members.count()>1):
            new_owner = User.query.get_or_404(request.form.get('new_owner'))
            success = transfer_ownership(project, new_owner)
            if not success:
                flash('Owner transfer unsuccessful.')
                return redirect(request.referrer)
        else:
            user_code = current_user.code
            manager.delete_project(project)
            flash(f'{project.name} deleted.')
            return user_page(user_code)
    manager.remove_user_from_project(current_user, project, admin=False)
    flash(f'You have left {project.name}.')
    return redirect(request.referrer)








@application.route('/change_project_status/<int:project_id>/<int:user_id>/<action>')
@login_required
@limiter.limit('20 per minute')
def change_project_status(project_id, user_id, action):
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    error_flag = False
    ## ACCEPT ##
    if action=='accept':
        if user in project.members:
            flash('Cannot accept user already in project.')
            error_flag = True
        else:
            manager.add_user_to_project(user, project)
    ## REJECT ##
    elif action=='reject':
        # remove user from project
        if user in project.members:
            manager.remove_user_from_project(user, project, admin=True)
        # remove user from pending
        else:
            error_flag = (not manager.reject_user_from_pending(user, project, admin=True))
    ## MAKE OWNER ##
    elif action=='make_owner':
        error_flag = (not transfer_ownership(project, user))
    else:
        flash('Invalid action.')
        error_flag = True
    if not error_flag:
        project.update_last_active()
        db.session.commit()
        db.session.close()
    return redirect(request.referrer)



@application.route('/collaborate/<int:target_user_id>', methods=['POST'])
@login_required
@limiter.limit('10/minute; 100/hour')
def collaborate(target_user_id):
    error_flag = False
    project = Project.query.get_or_404(request.form.get('selected_project'))
    target_user = User.query.get_or_404(target_user_id)
    if not current_user==project.owner:
        flash('Cannot invite collaborator to project you do not own.')
    elif current_user==target_user:
        flash("You don't need to send an invitation to collaborate with "
              "yourself!")
    elif not target_user.accepted:
        flash(f'{target_user.name} user has not been accepted to TheProjectProject yet.')
    elif target_user in project.members:
        flash(f'{target_user.name} is already a member of {project.name}.')
    elif target_user.has_applied(project):
        flash(f'{target_user.name} has already applied to {project.name}. '
            'Go to the project page to accept their application.')
    elif target_user in project.invitations:
        flash(f'You have already invited {target_user.name} to join '
              f'{project.name}. You will be notified when they respond.')
    else:
        target_user.invitations.append(project)
        notifcation = Notification(text=f'{current_user.name} has invited you '
                                        f'to collaborate on {project.name}! '
                                        'Visit your profile page to reply.')
        target_user.notifications.append(notifcation)
        flash(f'You have sent {target_user.name} an invitation to collaborate '
              f'on {project.name}. You will be notified when they respond.')
        project.update_last_active()
        db.session.commit()
        db.session.close()
    return redirect(request.referrer)


@application.route('/accept_collaboration/<int:project_id>')
@login_required
@limiter.limit('60 per minute')
def accept_collaboration(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user in project.invitations:
        flash(f'You have accepted the invitation to {project.name}.')
        manager.add_user_to_project(current_user, project)
    else:
        flash(f'Could not join {current_user.name} as you have not been invited.')
    return redirect(request.referrer)


@application.route('/reject_collaboration/<int:project_id>')
@login_required
def reject_collaboration(project_id):
    project = Project.query.get_or_404(project_id)
    manager.reject_project_invitation(current_user, project, admin=False)
    return redirect(request.referrer)


@application.route('/withdraw_collaboration/<int:user_id>/<int:project_id>')
@login_required
def withdraw_collaboration(user_id, project_id):
    user = User.query.get_or_404(user_id)
    project = Project.query.get_or_404(project_id)
    project.update_last_active()
    manager.reject_project_invitation(user, project, admin=True)
    return redirect(request.referrer)


@application.route('/withdraw_application/<int:project_id>')
@login_required
def withdraw_application(project_id):
    project = Project.query.get_or_404(project_id)
    project.update_last_active()
    manager.reject_user_from_pending(current_user, project, admin=False)
    flash(f'You have withdrawn your application to {project.name}.')
    return redirect(request.referrer)



@application.route('/complete_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('3 per minute')
def complete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can mark a project as complete.')
    else:
        project.update_last_active()
        manager.complete_project(project)
    return redirect(request.referrer)


@application.route('/uncomplete_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('3 per minute')
def uncomplete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can mark a project as incomplete.')
    else:
        project.update_last_active()
        manager.uncomplete_project(project)
    return redirect(request.referrer)


@application.route('/change_project_open/<int:project_id>/<action>', methods=['POST'])
@login_required
@limiter.limit('5 per minute')
def change_project_open(project_id, action):
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can change join settings.')
    elif action=='open':
        project.update_last_active()
        manager.open_project(project)
    elif action=='close':
        project.update_last_active()
        manager.close_project(project)
    return redirect(request.referrer)


@application.route('/add_application/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_application(project_id):
    project = Project.query.get_or_404(project_id)
    form = forms.Edit_Project_Application(request.form)
    if current_user!=project.owner:
        flash('Only the owner can change application settings.')
    elif form.validate_on_submit():
        project.update_last_active()
        manager.add_application(project, form.application_question.data)
    else:
        flash(f'Could not add application: {form.errors[0]}.')
    return redirect(request.referrer)


@application.route('/remove_application_requirement/<int:project_id>', methods=['POST'])
@login_required
def remove_application_requirement(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can change application settings.')
    else:
        project.update_last_active()
        manager.remove_application_requirement(project)
    return redirect(request.referrer)


if __name__ == '__main__':
    application.run(host='127.0.0.1')
