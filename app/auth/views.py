from flask import (
    current_app, request, redirect, url_for, render_template, flash, abort,
)
from flask_babel import gettext
from flask_login import login_user, login_required, logout_user
from itsdangerous import URLSafeSerializer, BadSignature
from app.extensions import lm
# from app.jobs import send_registration_email
from app.models import User
# from app.user.forms import RegisterUserForm
from .forms import Login
from ..auth import auth


@lm.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect(request.args.get('next') or url_for('home'))
    start_on = 0
    for i, elt in enumerate(form):
        if elt.errors:
            start_on = i
            break
    return render_template('login.html', form=form, start_on=start_on)


@application.route('/logout')
@login_required
def logout():
    current_user.active = False
    current_user.last_active = datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))
