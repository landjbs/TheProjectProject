from flask import request, redirect, url_for, render_template, flash, jsonify, g, get_template_attribute
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
from collections import Counter # # TEMP: COUNTER SHOULD BE MOVED OR REPLACED
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query, filter_string
from app.competition.models import Competition
from app.subject.models import Subject
from app.user.models import User
from app.link.forms import Add_Link

# # TODO: build custom package form with javascript tagging mechanism
from app.project.forms import Add_Project

# package imports
from .forms import Add_Shared, Add_Company

from ..add import add


@add.route('/add', methods=['GET','POST'])
@add.route('/add/<int:competition_id>', methods=['GET','POST'])
# @login_required
def add(competition_id=None):
    form = Add_Shared()
    form.subjects.choices = [(s.id, s) for s in Subject.query.all()]
    # form.competition.choices = Competition.recommend()
    return render_template('new_add.html', form=form, company=Add_Company())


@add.route('/next_fragement', methods=['POST'])
def next_fragement():
    form = Add_Shared()
    if form.validate_on_submit():
        return jsonify('true')
    return jsonify('false')
