from flask import request, redirect, url_for, render_template, flash, g
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# package imports
from .models import Message, Channel
from .forms import Message_Form
from ..message import message


@message.route('/messages')
@login_required
def messages():
    current_user.send_message('Bap bop boop!!!', to=[current_user])
    return render_template('messages.html')


@message.route('/send_message/<int:channel_id>', methods=['POST'])
@login_required
def send_message(channel_id):
    form = Message_Form()
    if form.validate_on_submit():
        Channel.get_by_id(channel_id).send(form.text.data, current_user)
    return redirect(request.referrer)
