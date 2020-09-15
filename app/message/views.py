from flask import request, redirect, url_for, render_template, flash, g
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# package imports
from .models import Message, Channel
from ..message import message


@message.route('/messages')
def messages():
    current_user.send_message('Bap bop boop!!!', to=[current_user])
    return render_template('messages.html')
