from flask import (Flask, render_template, request, flash, redirect,
                   url_for, session)
from flask_login import current_user, login_user, logout_user, login_required

from application import db
from application.models import User
from application.forms import Apply, Login

# Elastic Beanstalk initalization
application = Flask(__name__, static_url_path='', static_folder='static')
application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
application.debug=True
# change this to your own value
application.secret_key = 'cC1YCIWOj9GgWspgNEo2'


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


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
        return render_template('thanks.html')
    return render_template('apply.html', form=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # return redirect(url_for(''))
        return render_template('results.html')
    form = Login(request.form)
    if request.method=='POST' and form.validate():
        user = None # TODO: QUERY USER FROM EMAIL
        if user is None:
            form.email.errors.append('Email not found.')
        elif not user.check_password(form.password.data):
            form.password.errors.append('Invalid password.')
            # application pending
        elif user.accepted==False:
                form.email.errors.append('Your application is under review—'
                                         'check back soon!')
        login_user(user)
        return render_template('results.html')
    return render_template('login.html')


@application.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    application.run(host='0.0.0.0')
