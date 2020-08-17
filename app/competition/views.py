from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from app.utils import partition_query

from .models import Competition

from ..competition import competition


@competition.route(f'/competition=<code>', methods=['GET', 'POST'])
@login_required
def competition_page(code):
    competition = Competition.query.filter_by(code=code).first_or_404()
    return render_template('competition.html', competition=competition)
