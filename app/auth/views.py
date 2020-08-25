from os import urandom
from flask import (current_app, request, redirect, url_for,
                   render_template, flash, abort, g)
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import BadSignature, SignatureExpired
from datetime import datetime

from app.extensions import lm, bcrypt, serializer
from app.jobs import (
    send_registration_email, send_confirmation_email, send_password_reset_email
)
from app.user.models import User
from app.subject.models import Subject
from .forms import Login, Apply, StartReset
from ..auth import auth


CONFIRM_SALT = urandom(16)
RESET_SALT = urandom(16)


@lm.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@auth.route('/apply', methods=['GET', 'POST'])
def apply():
    # form preprocessing
    form = Apply()
    form.subjects.choices = [(s.id, s.name) for s in Subject.query.all()]
    # form validation
    if form.validate_on_submit():
        subjects = [Subject.query.get(int(id)) for id in form.subjects.data]
        user = User.create(
                    name=form.data['name'],
                    email=form.data['email'],
                    password=form.data['password'],
                    about=form.data['about'],
                )
        user.add_subjects(subjects, user_selected=True)
        if current_app.config['REGISTER_MAIL']:
            # generate token and send to user email
            token = serializer.dumps(user.id, salt=CONFIRM_SALT)
            url = url_for('auth.verify', token=token, _external=True)
            send_registration_email(user, url)
            # notify user and redirect to index
            flash(f'Congratulations, {user.name}, your application to '
                   'TheProjectProject has been submitted! '
                   'Please confirm your email by following the link we just sent you.',
                   category='success')
        else:
            flash('You have been accepted to TheProjectProject.')
            user.confirmed = True
            user.accept()
        return redirect(url_for('base.index'))
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('apply.html', form=form, start_on=start_on)


@auth.route('/verify/<token>', methods=['GET'])
def verify(token, expiration=604800):
    '''
    Verifies token from confirmation application
    Args:
        token:      URLSafeTimedSerializer token from apply()
        expiration: Seconds until expiration
    '''
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        id = s.loads(token, salt=CONFIRM_SALT, max_age=expiration)
    except SignatureExpired:
        # NOTE: RACE CONDITION IF DELETION AND CONFIRMATION HAPPEN SIMULTANEOUSLY
        # TODO: ACTUALLY REMOVE APPLICATION VERY IMPORTANT
        # notify user and redirect to application page
        flash(('Oops! Your email confirmation expired so we removed your ' \
               'application. Please apply again.'), category='error')
        return redirect(url_for('auth.apply'))
    except BadSignature:
        abort(404)
    user = User.query.filter_by(id=id).first_or_404()
    if user.confirmed:
        abort(404)
    user.confirmed = True
    send_confirmation_email(user)
    user.update()
    flash('You have confirmed your application! We will email you with '
          'application updates as soon as possible.', category='success')
    return redirect(url_for('base.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        current_user.active = True
        current_user.update()
        current_user.update_badges()
        return redirect(request.args.get('next') or url_for('hub.home'))
    form = Login()
    if form.validate_on_submit():
        user = form.user
        login_user(user)
        user.active = True
        user.last_active = datetime.utcnow()
        user.update_badges()
        user.update()
        return redirect(request.args.get('next') or url_for('hub.home'))
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('login.html', form=form, start_on=start_on)


@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    form = StartReset()
    if form.validate_on_submit():
        user = form.user
        token = serializer.dumps(user.id, salt=RESET_SALT)
        url = url_for('auth.reset_end', token=token, _external=True)
        send_password_reset_email(form.email.data, user.name, url)
        flash('A password reset link has been sent to your email.')
        return redirect(url_for('base.index'))
    return render_template('reset_start.html', form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset():
    form = StartReset()
    if form.validate_on_submit():
        user = form.user
        token = serializer.dumps(user.id, salt=RESET_SALT)
        url = url_for('auth.reset_end', token=token, _external=True)
        send_password_reset_email(form.email.data, user.name, url)
        flash('A password reset link has been sent to your email.')
        return redirect(url_for('base.index'))
    return render_template('reset_start.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    current_user.active = False
    current_user.last_active = datetime.utcnow()
    current_user.update()
    logout_user()
    return redirect(url_for('base.index'))
