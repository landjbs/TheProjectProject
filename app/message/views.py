import datetime
from flask import request, redirect, url_for, render_template, flash, g, jsonify, get_template_attribute
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# absolute imports
from app.user.models import User
# package imports
from .models import Message, Channel
from .forms import Message_Form
from ..message import message


# view
@message.route('/messages')
@login_required
def messages():
    return render_template('messages.html')


@message.route('/check_messages', methods=['GET'])
@login_required
def check_messages():
    since = request.args.get('since', type=float) + 1
    channel_id = request.args.get('channel', type=int)
    since = datetime.datetime.fromtimestamp(since)
    channel = Channel.query.get_or_404(channel_id)
    if not channel.is_member(current_user):
        raise PermissionError('')
    new_messages = channel.messages.filter(
                Message.timestamp > since
            ).order_by(Message.timestamp.asc())
    render_message = get_template_attribute(
                        'macros/chat.html', 'render_message'
                    )
    message_data = {'last_sent' : False}
    print(f'{current_user.name}: {new_messages.all()}')
    return jsonify([
        (
            render_message(m, message_data, sent_by_me=False),
            m.timestamp.timestamp()
        )
        for m in new_messages[::-1]
        if not m.sender==current_user
    ])


@message.route('/open_single_channel', methods=['POST'])
@login_required
def open_single_channel():
    user_id = int(request.json.get('user_id'))
    members = [User.get_by_id(user_id), current_user]
    channel = Channel.new(users=members)
    render_channel = get_template_attribute(
                        'macros/chat.html', 'render_channel'
                    )
    html = render_channel(channel)
    return jsonify({'html':html})


@message.route('/send_message', methods=['POST'])
@login_required
def send_message():
    # if not None:
    channel_id = int(request.json.get('channel_id'))
    channel = Channel.query.get_or_404(channel_id)
    html = ''
    if not channel.is_member(current_user):
        flash('Could not message because you are not a member of this channel.')
    else:
        text = str(request.json.get('text'))
        if text is not None:
            message = channel.send(text, current_user)
            # import macros for rendering messages
            render_message = get_template_attribute(
                                'macros/chat.html', 'render_message'
                            )
            message_data = {'last_sent' : channel.messages[1].timestamp}
            html = render_message(message, message_data, sent_by_me=True)
    return jsonify({'html':html})
