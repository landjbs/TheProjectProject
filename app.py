import numpy as np
from sqlalchemy import asc, desc
from sqlalchemy.sql.expression import func
from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import (current_user, login_user, logout_user,
                         login_required, LoginManager)
from datetime import datetime
from dateutil import tz
from collections import Counter
from operator import itemgetter

from application import db
from application.models import (User, Project, Comment, Task, Subject)
from application.forms import (Apply, Login, Add_Project, Comment_Form,
                                Task_Form, Project_Application)
import manager as manager


ADMIN_EMAIL = 'lkj;lsdjkf;laksdjf;lajsd;lfkj23lj2451@$%j12l4kj5lsakjfd;.'
ADMIN_PASSWORD = 'asdadsflkj;2kl4j51@$L%jldfka;skf,3m,.rmbnmdnbfd;.'

# login
login_manager = LoginManager()

# Elastic Beanstalk initalization
application = Flask(__name__, static_url_path='', static_folder='static')
application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
application.debug=True
# change this to your own value
application.secret_key = 'cC1YCIWOj9GgWspgNEo2'


# initalization
login_manager.init_app(application)


def is_project_member(user, project):
    if user==None:
        return False
    return (user in project.members)


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
        time = f"{time.strftime('%B %d, %Y')} at {time.strftime('%I:%M %p')}"
        time = time.lstrip("0").replace(" 0", " ")
        return time
    def complete(tasks):
        return tasks.filter_by(complete=True)
    def not_complete(tasks):
        return tasks.filter_by(complete=False)
    def is_project_member_(user, project):
        return is_project_member(user, project)
    return dict(calc_days_since=calc_days_since, calc_days_left=calc_days_left,
                elapsed_style=elapsed_style, time_to_str=time_to_str,
                not_complete=not_complete, complete=complete,
                is_project_member=is_project_member_)


def tasks_to_daily_activity(tasks):
    current_time = datetime.utcnow()
    start_stamps = []
    end_stamps = []
    for task in tasks:
        start_stamps.append(round((current_time-task.post_stamp).seconds * (1/(60**2)) ))
        # start_stamps.append((current_time-task.post_stamp).days)
        if task.complete:
            end_stamps.append(round(((current_time-task.complete_stamp).seconds * (1/(60**2)) )))
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
    return (start_activity, end_activity, earliest)


# querying
def query_user_by_id(id):
    return db.session.query(User).get(int(id))


def query_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()


@login_manager.user_loader
def load_user(id):
    return query_user_by_id(id)


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@application.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@application.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@application.route('/terms', methods=['GET', 'POST'])
def terms():
    return render_template('terms.html')


@application.route('/apply', methods=['GET', 'POST'])
def apply():
    form = Apply(request.form)
    if request.method=='POST' and form.validate():
        user = User(name        =       form.data['name'],
                    email       =       form.data['email'],
                    password    =       form.data['password'],
                    subjects    =       None,
                    github      =       form.data['github'],
                    about       =       form.data['about']
                )
        try:
            db.session.add(user)
            db.session.commit()
            db.session.close()
        except Exception as e:
            db.session.rollback()
        return render_template('index.html')
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('apply.html', form=form, start_on=start_on)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = Login(request.form)
    if request.method=='POST' and form.validate():
        user = query_user_by_email(form.email.data)
        if user is None:
            form.email.errors.append('Email not found.')
        elif not user.check_password(form.password.data):
            form.password.errors.append('Invalid password.')
            # application pending
        elif user.accepted==False:
                form.email.errors.append('Your application is under review—'
                                         'check back soon!')
        else:
            login_user(user)
            return home()
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('login.html', form=form, start_on=start_on)


# TODO: MAKE SECURE
@application.route('/admin', methods=['GET', 'POST'])
def admin():
    users = db.session.query(User)
    return render_template('admin.html', users=users)


@application.route('/accept', methods=['POST'])
def accept():
    user = query_user_by_id(request.form['accept'])
    setattr(user, 'accepted', True)
    db.session.commit()
    return admin()


@application.route('/reject', methods=['POST'])
def reject():
    user = query_user_by_id(request.form['reject'])
    setattr(user, 'accepted', False)
    db.session.commit()
    return admin()

## HOME ##
def partition_query(l, n=3):
    try:
        c = l.count()
    except:
        c = len(l)
    for i in range(0, c, n):
        yield l[i:i+n]


@login_required
@application.route('/home', methods=['GET', 'POST'])
def home():
    # recommended projects
    recs = db.session.query(Project).filter(Project.owner!=current_user).limit(30)
    recommended_tabs = list(partition_query(recs))
    # top projects
    tops = db.session.query(Project).order_by(desc(Project.buzz)).limit(9)
    top_tabs = partition_query(tops)
    # user projects
    user_projs = db.session.query(Project).filter_by(owner=current_user).limit(9)
    user_tabs = partition_query(user_projs)
    project_application = Project_Application(request.form)
    return render_template('home.html', recommended_tabs=recommended_tabs,
                            top_tabs=top_tabs, user_tabs=user_tabs,
                            user_project_count=user_projs.count(),
                            current_user=current_user,
                            project_application=project_application)


@login_required
@application.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = Add_Project(request.form)
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
                    manager.create_project(project, current_user)
                    db.session.commit()
                    db.session.close()
                except Exception as e:
                    print(f'ERROR: {e}')
                    db.session.rollback()
                    return render_template('add_project.html', form=form)
                return redirect(url_for('home'))
    return render_template('add_project.html', form=form)


@login_required
@application.route('/user=<email>')
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
    # worked tasks
    tasks = user.tasks_worked
    task_data = {} if (len(tasks)>0) else None
    if task_data is not None:
        _, end_activity, earliest = tasks_to_daily_activity(tasks)
        task_data['end_activity'] = end_activity
        task_data['earliest'] = earliest
    # owned projects
    owned = user.owned
    owned_tabs = partition_query(owned)
    # member projects
    member_projects = [project for project in user.projects
                       if not project in owned]
    member_tabs = partition_query(member_projects)
    # sum stars and aggregate subjects
    stars = 0
    subjects = []
    for project in user.projects:
        stars += project.stars.count()
        subjects += [subject.name for subject in project.subjects]
    subject_data = Counter(subjects) if subjects!=[] else False
    return render_template('user.html', user=user, stars=stars,
                            task_data=task_data, subject_data=subject_data,
                            owned_tabs=owned_tabs, member_tabs=member_tabs)


@login_required
@application.route('/project=<project_name>')
def project(project_name):
    project = Project.query.filter_by(name=project_name).first_or_404()
    comment_form = Comment_Form(request.form)
    task_form = Task_Form(request.form)
    ## task data visualization ##
    # vis activity
    activity_data = {} if project.tasks.count()>0 else False
    if activity_data != False:
        start_activity, end_activity, earliest = tasks_to_daily_activity(project.tasks)
        activity_data['start_activity'] = start_activity
        activity_data['end_activity'] = end_activity
        activity_data['earliest'] = earliest
    # compile counts of tasks completed by each worker
    completers = []
    for task in project.tasks.filter_by(complete=True):
        for worker in task.workers:
            completers.append(worker)
    # select top 5 to plot
    task_data = Counter(completers)
    ## subject visualization ##
    # TODO:
    role_data = {}
    filled_data = {}
    return render_template('project.html', project=project,
                            now=datetime.utcnow, comment_form=comment_form,
                            task_form=task_form,
                            activity_data=activity_data,
                            task_data=task_data,
                            role_data=role_data, filled_data=filled_data)


@login_required
@application.route('/subject=<subject_name>')
def subject(subject_name):
    subject = Subject.query.filter_by(code=subject_name).first_or_404()
    # project tabs
    subject_projects = Project.query.filter(Project.subjects.contains(subject)).limit(300)
    project_tabs = partition_query(subject_projects)
    # users
    user_tabs = []
    subject_tabs = []
    return render_template('search.html', project_tabs=project_tabs,
                        user_tabs=user_tabs, subject_tabs=subject_tabs,
                        search_text=subject.name)


@login_required
@application.route('/join_project/<int:project_id>')
def join_project(project_id):
    project = Project.query.get_or_404(project_id)
    if is_project_member(current_user, project):
        flash(f'Could not join {project.name} because you are '
                'already a member.')
        return redirect(request.referrer)
    form = Project_Application(request.form)
    if form.validate_on_submit():
        if project.open:
            if not project.requires_application:
                current_user.projects.append(project)
                flash(f'You have been added to {project.name}!')
            else:
                project.pending_members.append(current_user)
                flash(f'Your application to {project.name} been submitted.')
            db.session.add(project)
            db.session.commit()
        else:
            flash('The project owner has closed this project.')
    return redirect(request.referrer)


@login_required
@application.route('/leave_project/<int:project_id>/<int:new_owner_id>')
def leave_project(project_id, new_owner_id):
    project = Project.query.get_or_404(project_id)
    if not is_project_member(current_user, project):
        flash(f'Cannot leave {project.name} without being a member.')
        return redirect(request.referrer)
    if (current_user == project.owner):
        flash(f'You have transferred ownership of {project.owner} to .')
        print('here')
    project.users.delete(current_user)
    db.session.commit()
    flash(f'You have left {project.name}.')
    return redirect(request.referrer)


@login_required
@application.route('/like/<int:project_id>/<action>')
def like_action(project_id, action):
    project = Project.query.get_or_404(project_id)
    if action == 'like':
        current_user.star_project(project)
        db.session.commit()
    if action == 'unlike':
        current_user.unstar_project(project)
        db.session.commit()
    return redirect(request.referrer)


@login_required
@application.route('/project/<int:project_id>/task', methods=['POST'])
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    if not is_project_member(current_user, project):
        return redirect(request.referrer)
    form = Comment_Form(request.form)
    if form.validate_on_submit():
        comment = Task(text=form.text.data, author=current_user, project=project)
        db.session.add(comment)
        db.session.commit()
    return redirect(request.referrer)


@login_required
@application.route('/project/<int:project_id>/comment', methods=['POST'])
def add_comment(project_id):
    project = Project.query.get_or_404(project_id)
    form = Comment_Form(request.form)
    if form.validate_on_submit():
        comment = Comment(text=form.text.data, author=current_user, project=project)
        db.session.add(comment)
        db.session.commit()
    return redirect(request.referrer)


@login_required
@application.route('/project/<int:project_id>/<int:comment_id>')
def delete_comment(project_id, comment_id):
    project = Project.query.get_or_404(project_id)
    comment = Comment.query.get_or_404(comment_id)
    if current_user in [project.owner, comment.author]:
        db.session.delete(comment)
        db.session.commit()
    else:
        flash('Cannot delete comment.')
    return redirect(request.referrer)


@application.route('/mark_complete/<int:project_id>/<int:task_id>/<action>')
@login_required
def mark_complete(project_id, task_id, action):
    project = Project.query.get_or_404(project_id)
    # screen non-members
    if not is_project_member(current_user, project):
        return redirect(request.referrer)
    # get task
    task = Task.query.get_or_404(task_id)
    if (action=='complete'):
        if not task.complete:
            task.mark_complete(current_user)
        else:
            task.add_worker(current_user)
    elif (action=='back'):
        if current_user in task.workers:
            task.workers.remove(current_user)
        if (len(task.workers)==0):
            task.mark_incomplete()
    elif (action=='delete'):
        if (current_user==task.author):
            db.session.delete(task)
    db.session.commit()
    return redirect(request.referrer)


@application.route('/change_project_status/<int:project_id>/<action>')
@login_required
def change_project_status(project_id, action):
    raise RuntimeError('change_project_status not implemented.')


@application.route('/search', methods=['POST'])
def search():
    search_text = request.form.get('search')
    # project results
    project_results = Project.query.filter(Project.name.contains(search_text) |
                                   Project.oneliner.contains(search_text))
    project_tabs = partition_query(project_results.limit(30))
    # user results
    user_results = User.query.filter(User.name.contains(search_text) |
                                     User.about.contains(search_text))
    user_tabs = partition_query(user_results.limit(30))
    # subject results
    subject_results = Subject.query.filter(Subject.name.contains(search_text))
    subject_tabs = partition_query(subject_results.limit(30))
    return render_template('search.html', project_tabs=project_tabs,
                        user_tabs=user_tabs, subject_tabs=subject_tabs,
                        search_text=search_text)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    application.run(host='0.0.0.0')
