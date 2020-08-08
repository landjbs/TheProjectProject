from flask import (current_app, request, redirect, url_for,
                   render_template, flash, abort)
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime

from app.extensions import lm
from app.jobs import send_registration_email, send_confirmation_email
from app.user.models import User
from .forms import Login, Apply
from ..auth import auth


@lm.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@auth.route('/apply', methods=['GET', 'POST'])
def apply():
    form = Apply()
    if form.validate_on_submit():
        user = User.create(
                    name=form.data['name'],
                    email=form.data['email'],
                    password=form.data['password'],
                    url=form.data['url'],
                    about=form.data['about']
                )
        # generate token and send to user email
        s = URLSafeSerializer(current_app.secret_key)
        token = s.dumps(user.id)
        url = url_for('auth.verify', token=token, _external=True)
        send_registration_email.queue(user, url)
        # notify user and redirect to index
        flash(f'Congratulations, {user.name}, your application to '
               'TheProjectProject has been submitted! '
               'A confirmation link has been sent to your email.')
        return redirect(url_for('base.index'))
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('apply.html', form=form, start_on=start_on)


@auth.route('/verify/<token>', methods=['GET'])
def verify(token):
    s = URLSafeSerializer(current_app.secret_key)
    try:
        id = s.loads(token)
    except BadSignature:
        abort(404)
    user = User.query.filter_by(id=id).first_or_404()
    if user.confirmed:
        abort(404)
    user.confirmed = True
    send_confirmation_email.queue(user)
    user.update()
    flash('You have confirmed your application! We will email you with '
          'application updates as soon as possible.')
    return redirect(url_for('base.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        current_user.active = True
        current_user.update()
        return redirect(request.args.get('next') or url_for('hub.home'))
    form = Login()
    if form.validate_on_submit():
        user = form.user
        login_user(user)
        user.active = True
        user.last_active = datetime.utcnow()
        user.update()
        return redirect(request.args.get('next') or url_for('hub.home'))
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('login.html', form=form, start_on=start_on)



@auth.route('/logout')
@login_required
def logout():
    current_user.active = False
    current_user.last_active = datetime.utcnow()
    current_user.update()
    logout_user()
    return redirect(url_for('base.index'))



# FROMAPPLICATION
# @application.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         current_user.active = True
#         db.session.commit()
#         return redirect(url_for('home'))
#     form = forms.Login(request.form)
#     if request.method=='POST' and form.validate():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user is None:
#             form.email.errors.append('Email not found.')
#         elif not user.check_password(form.password.data):
#             form.password.errors.append('Invalid password.')
#         elif user.accepted==False:
#                 form.email.errors.append('Your application is under review—'
#                                          'check back soon!')
#         else:
#             login_user(user)
#             user.active = True
#             user.last_active = datetime.utcnow()
#             db.session.commit()
#             return home()
#     start_on = 0
#     for i, elt in enumerate(form):
#         if elt.errors:
#             start_on = i
#             break
#     return render_template('login.html', form=form, start_on=start_on)
