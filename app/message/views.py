from flask import request, redirect, url_for, render_template, flash, g
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# absolute imports
from app.user.models import User
# package imports
from .models import Message, Channel
from .forms import Edit_User
from ..message import message


@message.route('/messages')
def messages():
    user = User.query.all()
    return render_template('messages.html', users=users, messages=message)
