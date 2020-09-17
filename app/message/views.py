from flask import request, redirect, url_for, render_template, flash, g, jsonify, get_template_attribute
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
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


@message.route('/send_message/<int:channel_id>', methods=['POST'])
@login_required
def send_message(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    if not channel.is_member(current_user):
        flash('Could not message because you are not a member of this channel.')
    else:
        text = str(request.json.get('data'))
        if text is not None:
            message = channel.send(text, current_user)
            # import macros for rendering messages
            def time_to_str(time):
                from_zone = tz.tzutc()
                to_zone = tz.tzlocal()
                time = time.replace(tzinfo=from_zone)
                time = time.astimezone(to_zone)
                # time = f"{time.strftime('%B %d, %Y')} at {time.strftime('%I:%M %p')}"
                time = f"{time.strftime('%B %d')}"
                time = time.lstrip("0").replace(" 0", " ")
                return time
            render_message = get_template_attribute(
                                'macros/chat.html', 'render_message',
                                time_to_str=time_to_str)
            html = render_template(render_message(message))
    html = None
    return jsonify({'html':html})
