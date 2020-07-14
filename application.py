from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import (current_user, login_user, logout_user,
                         login_required, LoginManager)

from application import db
from application.models import User, Project
from application.forms import Apply, Login, Add_Project


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
            print(f'EASDF: {e}')
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
@login_required
@application.route('/home', methods=['GET', 'POST'])
def home():
    projects = db.session.query(Project).limit(9)
    project_tabs = [projects[:3], projects[3:6], projects[6:9]]
    return render_template('home.html', projects=project_tabs,
                           current_user=current_user)


@login_required
@application.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = Add_Project(request.form)
    if request.method=='POST' and form.validate():
        # dependent errors
        if form.requires_application.data and form.application_question.data=='':
            form.application_question.errors = ['Question cannot be blank.']
        # add the project
        else:
            project = Project(name = form.name.data,
                          summary = form.summary.data,
                          url = form.url.data,
                          creator = current_user,
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


@application.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(name=username).first_or_404()
    return render_template('index.html', user=user)


@application.route('/project/<project_name>')
@login_required
def project(project_name):
    project = Project.query.filter_by(name=project_name).first_or_404()
    return render_template('index.html', project=project)



if __name__ == '__main__':
    application.run(host='0.0.0.0')
