from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from ..badge import badge



@user.route('/badge', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def badge_page():
    # update badges
    current_user.update_badges(['SuperOwner', 'Verified'])
    # badges in progress
    # all badges
    return render_template('badge.html')
