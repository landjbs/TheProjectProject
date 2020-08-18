from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized

from app.extensions import limiter
from app.utils import partition_query

from app.competition.models import Competition

from .models import Badge
from ..badge import badge


def badge_page():
    # active competitions
    competitions = Competition.get_active_competitions()
    # update badges
    current_user.update_badges()
    # all badges
    all_tabs = list(partition_query(Badge.query.all()))
    return render_template('badge.html',
                            competitions=competitions,
                            all_tabs=all_tabs)
