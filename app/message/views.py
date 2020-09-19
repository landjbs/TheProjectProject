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
    from app.user.models import User
    User.get_by_id(2).send_message('Bap bop boop!!!', to=[current_user])
    return render_template('messages.html')


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
    print(html)
    return jsonify({'html':html})


@message.route('/send_message/', methods=['POST'])
@message.route('/send_message/<int:channel_id>', methods=['POST'])
@login_required
def send_message(channel_id=None):
    if not None:
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
            html = render_message(message, sent_by_me=True)
    return jsonify({'html':html})
