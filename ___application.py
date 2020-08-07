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



if __name__ == '__main__':
    application.run(host='127.0.0.1')
