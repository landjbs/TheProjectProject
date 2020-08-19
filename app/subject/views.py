from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# absolute imports
from app.utils import partition_query
from app.project.models import Project
from app.project.forms import Project_Application_Form
# relative imports
from .models import Subject
# blueprint
from ..subject import subject


@subject.route('/subject=<subject_name>')
@login_required
def subject_page(subject_name):
    subject = Subject.query.filter_by(code=subject_name).first_or_404()
    # projects
    projects = Project.query.filter(Project.subjects.contains(subject)).all()
    # users
    users = [s.user for s in subject.users[:30]]
    # template
    return render_template('subject.html',
                           projects=projects,
                           users=users,
                           subject=subject)
