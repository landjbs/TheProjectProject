from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized

from app.extensions import limiter
from app.utils import partition_query

from .models import Badge
from ..badge import badge


def badge_page():
    # update badges
    current_user.update_badges()
    # progress tabs
    progress_tabs = list(partition_query(current_user.badges))
    # all badges
    all_tabs = list(partition_query(Badge.query.all()))
    return render_template('badge.html',
                            progress_tabs=progress_tabs,
                            all_tabs=all_tabs)


@badge.route('/badge', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
@mobilized(badge_page)
def badge_page():
    ''' Mobile optimized badge page '''
    # update badges
    current_user.update_badges()
    # progress tabs
    progress_badges = list(current_user.badges)
    # all badges
    all_badges = list(Badge.query.all())
    return render_template('badge_mobile.html',
                        progress_badges=progress_badges,
                        all_badges=all_badges)
