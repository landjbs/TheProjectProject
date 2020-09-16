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


@message.route('/send_message', methods=['POST'])
@login_required
def send_message():
    form = Message_Form()
    if form.validate_on_submit():
        print(form.text.data)
    # channel.send_message()
    return redirect(request.referrer)
