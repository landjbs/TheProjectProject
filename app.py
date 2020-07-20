from sqlalchemy import asc, desc
from sqlalchemy.sql.expression import func
from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import (current_user, login_user, logout_user,
                         login_required, LoginManager)
from datetime import datetime
from dateutil import tz
from collections import Counter

from application import db
from application.models import User, Project, Comment, Task
from application.forms import Apply, Login, Add_Project, Comment_Form, Task_Form


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


# functions
@application.context_processor
def utility_processor():
    def calc_days_since(now, start):
        return int((now - start).days + 3)
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
    return dict(calc_days_since=calc_days_since, calc_days_left=calc_days_left,
                elapsed_style=elapsed_style, time_to_str=time_to_str,
                not_complete=not_complete, complete=complete)


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
    if current_user.is_authenticated:
        if current_user.accepted:
            return redirect(url_for('home'))
        else:
            print('Not accepted')
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
    for i in range(0, l.count(), n):
        yield l[i:i+n]


@login_required
@application.route('/home', methods=['GET', 'POST'])
def home():
    # recommended projects
    recs = db.session.query(Project).limit(30)
    recommended_tabs = partition_query(recs)
    # top projects
    tops = db.session.query(Project).order_by(desc(Project.buzz)).limit(9)
    top_tabs = partition_query(tops)
    # user projects
    users_projs = db.session.query(Project).filter_by(owner=current_user).limit(9)
    users_tabs = partition_query(recs)
    return render_template('home.html', recommended_tabs=recommended_tabs,
                            top_tabs=top_tabs, users_tabs=users_tabs,
                            current_user=current_user)


@login_required
@application.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = Add_Project(request.form)
    if request.method=='POST' and form.validate():
        error_flag = False
        # dependent errors
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
        # add the project
        if not error_flag:
            project = Project(name = form.name.data,
                          oneliner=form.oneliner.data,
                          summary = form.summary.data,
                          url = form.url.data,
                          owner = current_user,
                          open = form.open.data,
                          requires_application = form.requires_application.data,
                          application_question = form.application_question.data,
                          estimated_time = form.estimated_time.data,
                          team_size = form.team_size.data,
                          complete = form.complete.data)
            try:
                db.session.add(project)
                db.session.commit()
                db.session.close()
            except Exception as e:
                print(f'ERROR: {e}')
                db.session.rollback()
            return redirect(url_for('home'))
    return render_template('add_project.html', form=form)


@application.route('/user=<email>')
@login_required
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
    return render_template('user.html', user=user)


@application.route('/project=<project_name>')
@login_required
def project(project_name):
    project = Project.query.filter_by(name=project_name).first_or_404()
    comment_form = Comment_Form(request.form)
    task_form = Task_Form(request.form)
    ## task data visualization ##
    # compile counts of tasks completed by each worker
    completers = []
    for task in project.tasks.filter_by(complete=True):
        for worker in task.workers:
            completers.append(worker)
    # select top 5 to plot
    task_data = Counter(completers)
    ## role data visualization ##
    roles, filled = [], []
    for member_role in project.members:
        for role in member_role.roles:
            if not role.name in ['Pending', 'Member']:
                roles.append(role)
                if not member_role.user is None:
                    filled.append(role)
    role_data = Counter(roles)
    filled_data = Counter(filled)
    return render_template('project.html', project=project,
                            now=datetime.utcnow(), comment_form=comment_form,
                            task_form=task_form, task_data=task_data,
                            role_data=role_data, filled_data=filled_data)


@application.route('/like/<int:project_id>/<action>')
@login_required
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


@application.route('/mark_complete/<int:project_id>/<int:task_id>/<action>')
@login_required
def mark_complete(project_id, task_id, action):
    project = Project.query.get_or_404(project_id)
    task = Task.query.get_or_404(task_id)
    if (action=='complete'):
        if not task.complete:
            task.mark_complete(current_user)
        else:
            task.add_worker(current_user)
        db.session.commit()
    elif (action=='uncomplete'):
        raise RuntimeError('uncomplete functionality not yet built.')
    return redirect(request.referrer)


@application.route('/search', methods=['POST'])
def search():
    return render_template('project.html', project=project)


@application.route('/test', methods=['GET', 'POST'])
def test():
    recs = db.session.query(Project).limit(30)
    recommended_tabs = partition_query(recs)
    return render_template('test.html', recommended_tabs=recommended_tabs)



if __name__ == '__main__':
    application.run(host='0.0.0.0')
