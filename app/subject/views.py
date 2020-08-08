from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
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
def subject(subject_name):
    subject = Subject.query.filter_by(code=subject_name).first_or_404()
    # project tabs
    subject_projects = Project.query.filter(Project.subjects.contains(subject)).limit(30)
    project_tabs = list(partition_query(subject_projects))
    # users
    subject_users = [s.user for s in subject.users[:30]]
    user_tabs = partition_query(subject_users)
    #
    subject_tabs = []
    # application
    project_application = Project_Application_Form()
    return render_template('hub.search.html', project_tabs=project_tabs,
                        user_tabs=user_tabs, subject_tabs=subject_tabs,
                        search_text=subject.name,
                        project_application=project_application)
