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
from app.project.models import Project
# from app.company.models import Company

# package imports
from .forms import Add_Shared

from ..add import add


@add.route('/add', methods=['GET', 'POST'])
@add.route('/add/<int:competition_id>', methods=['GET', 'POST'])
# @login_required
def add_page(competition_id=None):
    form = Add_Shared(request.form)
    form.subjects.choices = [(s.id, s) for s in Subject.query.all()]
    form.competition.choices = Competition.recommend()
    if form.validate_on_submit():
        subjects = [Subject.query.get(int(id)) for id in form.subjects.data]
        if form.competition.data:
            competition = Competition.query.get(int(form.competition.data))
        else:
            competition = None
        # determine type of object to build
        if form.type.data=='1':
            project = Project.build_from_form(form, owner=current_user)
            return jsonify({
                'html': url_for('project.project_page', project_code=project.code)
            })
        elif form.type.data=='2':
            obj = Company.build_from_form(form)
        else:
            raise ValueError('Invalid type.')
        return jsonify({
            'path': url_for('hub.home')
        })
    elif form.errors:
        for field in form:
            print(field.name, field.errors)
        return jsonify({
            'errors':   form.errors
        })
    return render_template('new_add.html', form=form)


# @add.route('/next_fragment', methods=['POST'])
# def next_fragment():
#     form = Add_Type()
#     print(f'DATA: {form.data}')
#     if form.validate_on_submit():
#         render_fragment = get_template_attribute(
#             'macros/forms/fragment.html', 'render_fragment'
#         )
#         return jsonify({
#             'html': render_fragment(form.get_next_fragment())
#         })
#     return jsonify('false')


# @add.route('/next_field', methods=['POST'])
# def next_field():
#     current_field = fields
