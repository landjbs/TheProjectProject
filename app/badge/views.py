from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from app.extensions import limiter
from app.utils import partition_query

from .models import Badge
from ..badge import badge



@badge.route('/badge', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def badge_page():
    # update badges
    current_user.update_badges()
    # progress tabs
    progress_tabs = partition_query(current_user.badges)
    # all badges
    all_tabs = partition_query(Badge.query.all())
    return render_template('badge.html',
                            progress_tabs=progress_tabs,
                            all_tabs=all_tabs)
