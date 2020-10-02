from flask import request, redirect, url_for, render_template, flash, jsonify, g, get_template_attribute
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
from collections import Counter # # TEMP: COUNTER SHOULD BE MOVED OR REPLACED
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query, filter_string
from app.competition.models import Competition
from app.user.models import User
from app.link.forms import Add_Link

# package imports


from ..add import add


@add.route('/new_add', methods=['GET','POST'])
@add.route('/new_add/<int:competition_id>', methods=['GET','POST'])
# @login_required
def new_add(competition_id=None):
    form = Add_Project(competition=competition_id)
    form.subjects.choices = [(s.id, s) for s in Subject.query.all()]
    form.competition.choices = Competition.recommend()
    return render_template('new_add.html', form=form)
