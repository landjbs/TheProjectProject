from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized

from ..notification import notification


@notification.route('/notifications')
def notifications():
    all_notes = []
    n_unseen = current_user.n_unseen()
    for note in current_user.notifications:
        note.mark_seen()
        all_notes.append(note)
    return render_template('notifications.html',
                        all_notes=all_notes,
                        n_unseen=n_unseen)
