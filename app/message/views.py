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

from sqlalchemy import func



# view
@message.route('/get_channel', methods=['POST'])
@login_required
def get_channel():
    channel_id = int(request.json.get('channel_id'))
    channel = Channel.get_and_validate(channel_id, current_user)
    render_channel = get_template_attribute(
                        'macros/chat.html', 'render_channel'
                    )
    html = render_channel(channel)
    return jsonify({
        'html'          : html,
        'channel_id'    : channel.id
    })


@message.route('/check_messages', methods=['GET'])
@login_required
def check_messages():
    ## get channel ##
    channel_id = request.args.get('channel', type=int)
    channel = Channel.get_and_validate(channel_id, current_user)
    ## get since ##
    since = request.args.get('since', 0, type=float)
    # check if valid since
    if (since==0):
        since = channel.most_recent()
        if since is False:
            since = 0
        else:
            since = since.timestamp()
        return jsonify({
            'new_messages'  : [],
            'since'         : since
        })
    # convert since to datetime for filtering
    since = datetime.datetime.fromtimestamp(since)
    user_id = current_user.id
    # query recent messages not sent by user
    new_messages = channel.messages.filter(
                Message.timestamp > since,
                Message.sender_id != user_id
            ).order_by(Message.timestamp.asc())
    render_message = get_template_attribute(
                        'macros/chat.html', 'render_message'
                    )
    data = channel.data()
    # update last read in user channel
    channel.users.query.filter_by(user=current_user).first().last_read = datetime.datetime.utcnow()
    return jsonify({
            'new_messages': [
                                render_message(m, data, sent_by_me=False)
                                for m in new_messages[::-1]
                            ],
            'since':        channel.most_recent().timestamp()
        })


@message.route('/n_new_messages', methods=['GET'])
def n_new_messages():
    n = current_user.n_new_messages()
    return jsonify({'n': n})


@message.route('/n_channel_messages', methods=['GET'])
@login_required
def n_channel_messages():
    ## get channel ##
    channel_id = request.args.get('channel', type=int)
    channel = Channel.get_and_validate(channel_id, current_user)
    ## return number sent in channel since last read ##
    n = channel.n_unseen(current_user)
    return n


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
    return jsonify({
        'html'          : html,
        'channel_id'    : str(channel.id)
    })


@message.route('/send_message', methods=['POST'])
@login_required
def send_message():
    channel_id = int(request.json.get('channel_id'))
    channel = Channel.get_and_validate(channel_id, current_user)
    html = ''
    text = str(request.json.get('text'))
    if text is not None:
        message = channel.send(text, current_user)
        # import macros for rendering messages
        render_message = get_template_attribute(
                            'macros/chat.html', 'render_message'
                        )
        html = render_message(message, channel.data(), sent_by_me=True)
    return jsonify({'html':html})


@message.route('/update_last_read', methods=['GET'])
@login_required
def update_last_read():
    ## get channel ##
    channel_id = int(request.args.get('channel_id'))
    channel = Channel.get_and_validate(channel_id, current_user)
    ## get user channel ##
    uc = channel.users.filter_by(user=current_user).first()
    timestamp = uc.update_last_read()
    return jsonify({
        'success' :     True,
        'timestamp' :   timestamp
    })
