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
    return render_template('subject.html',
                           projects=projects,
                           users=users,
                           subject=subject)


def subject_page(subject_name):
    ''' Mobile optimized route for subject page '''
    subject = Subject.query.filter_by(code=subject_name).first_or_404()
    # projects
    subject_projects = Project.query.filter(Project.subjects.contains(subject))
    project_count = subject_projects.count()
    # users
    user_count = len(subject.users)
    subject_users = [s.user for s in subject.users[:30]]
    # format result data
    results = {'project'    :   (list(subject_projects), project_count),
               'user'       :   (list(subject_users), user_count)}
    # form
    project_application = Project_Application_Form()
    return render_template('subject_mobile.html',
                        results=results,
                        subject=subject,
                        user_results=subject_users)
