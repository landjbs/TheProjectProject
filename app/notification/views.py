from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized

from ..notification import notification


@notification.route('/notifications')
def notifications():
    all_notes = [x for x in current_user.notifications]
    print([x.text for x in all_notes])
    return render_template('notifications.html', all_notes=all_notes)
