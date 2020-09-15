from flask import request, redirect, url_for, render_template, flash, g
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# package imports
from .models import Message, Channel
from .forms import Edit_User
from ..message import message


@message.route('/messages')
def messages():
    current_user.messages.append()
    current_user.update()
