from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized

from app.extensions import limiter
from app.utils import partition_query

from app.competition.models import Competition

from .models import Badge
from ..badge import badge


@badge.route('/perks', methods=['GET'])
@login_required
@limiter.limit('')
def perk_page():
    # active competitions
    competitions = list(Competition.get_active_competitions().all())
    # update badges
    current_user.update_badges()
    # all badges currently in progress
    my_badges = list(current_user.badges)
    # all badges
    other_badges = list(Badge.query.all())
    return render_template('badge.html',
                            competitions=competitions,
                            my_badges=my_badges,
                            other_badges=other_badges)
