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
