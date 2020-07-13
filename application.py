from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import (current_user, login_user, logout_user,
                         login_required, LoginManager)

from application import db
from application.models import User, Project
from application.forms import Apply, Login


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
    # if current_user.is_authenticated:
    #     print(current_user)
    #     print(current_user.accepted)
    #     if current_user.accepted:
    #         return redirect(url_for('home'))
    #     else:
    #         print('Not accepted')
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


@login_required
@application.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


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


@application.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    application.run(host='0.0.0.0')
