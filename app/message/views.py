from flask import request, redirect, url_for, render_template, flash, g, jsonify
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# package imports
from .models import Message, Channel
from .forms import Message_Form
from ..message import message


@message.route('/messages')
@login_required
def messages():
    from app.user.models import User
    User.get_by_id(2).send_message('Bap bop boop!!!', to=[current_user])
    return render_template('messages.html')


@message.route('/send_message/<int:channel_id>', methods=['POST'])
@login_required
def send_message(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    if not channel.is_member(current_user):
        flash('Could not message because you are not a member of this channel.')
    else:
        message = str(request.json.get('data'))
        if message is not None:
            channel.send(message, current_user)
    return jsonify({})
    # return redirect(request.referrer)
