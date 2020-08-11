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


def subject_page(subject_name):
    subject = Subject.query.filter_by(code=subject_name).first_or_404()
    # project tabs
    subject_projects = Project.query.filter(Project.subjects.contains(subject))
    project_count = subject_projects.count()
    project_tabs = list(partition_query(subject_projects.limit(30)))
    # users
    user_count = len(subject.users)
    subject_users = [s.user for s in subject.users[:30]]
    user_tabs = partition_query(subject_users)
    # application
    project_application = Project_Application_Form()
    return render_template('subject.html',
                           project_tabs=project_tabs,
                           project_count=project_count,
                           user_tabs=user_tabs,
                           user_count=user_count,
                           subject=subject,
                           project_application=project_application)


@subject.route('/subject=<subject_name>')
@login_required
@mobilized(subject)
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
    results = {'project'    :   (subject_projects, project_count),
               'user'       :   (subject_users, user_count)}
    # form
    project_application = Project_Application_Form()
    return render_template('subject_mobile.html',
                        results=results,
                        subject=subject,
                        user_results=subject_users)
