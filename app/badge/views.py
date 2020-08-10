from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from .models import Badge

from ..badge import badge



@user.route('/badge', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def badge_page():
    # update badges
    current_user.update_badges()
    # all badges
    all_badges = Badge.query.all()
    return render_template('badge.html', all_badges)
