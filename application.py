from flask import Flask, render_template, request
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


# def index():
#     form1 = Apply(request.form)
#     form2 = RetrieveDBInfo(request.form)
#
#     if request.method == 'POST' and form1.validate_on_submit():
#         data_entered = Data(name=form1.data['name'],
#                             email=form1.data['email'],
#                             password=form1.data['password'],
#                             github=form1.data['github'],
#                             about=form1.data['about'])
#         try:
#             db.session.add(data_entered)
#             db.session.commit()
#             db.session.close()
#         except Exception as e:
#             print(f'ERROR: {e}')
#             db.session.rollback()
#         return render_template('thanks.html', notes=form1.data['name'])
#
#     if request.method == 'POST' and form2.validate():
#         try:
#             num_return = int(form2.numRetrieve.data)
#             query_db = Data.query.order_by(Data.id.desc()).limit(num_return)
#             for q in query_db:
#                 print(f'NAME: {q.name}')
#             db.session.close()
#         except:
#             db.session.rollback()
#         return render_template('results.html', results=query_db,
#                                num_return=num_return)
#
#     return render_template('index.html', form1=form1, form2=form2)


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
    form = Login(request.form)
    if request.method=='POST' and form.validate():

    return render_template('login.html')


@application.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    application.run(host='0.0.0.0')
