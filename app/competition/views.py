from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from .models import Competition

from ..competition import competition


@competition.route(f'/competition=<code>', methods=['GET'])
@login_required
def competition_page(code):
    competition = Competition.query.get_or_404(code)
    return render_template('competition.html', competition=competition)
