from flask import (current_app, request, redirect, url_for,
                   render_template, flash, abort)
from flask_login import current_user, login_required
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime

from ..hub import hub
from app.utils import partition_query
from app.recommendations.projects import (get_recommended_projects,
                                    get_trending_projects, get_user_projects)


@hub.route('/home', methods=['GET'])
@login_required
def home():
    # recommended projects
    recommended_projects = get_recommended_projects(current_user)
    recommended_tabs = list(partition_query(recommended_projects))
    # top projects
    trending_projects = get_trending_projects()
    trending_tabs =  list(partition_query(trending_projects))
    # user projects
    user_projects = get_user_projects(current_user)
    user_tabs = list(partition_query(user_projects))
    project_application = None #forms.Project_Application_Form(request.form)
    # notifcations
    # if (current_user.notifications.count())>0:
    #     for notification in current_user.notifications:
    #         flash(notification.text)
    #         current_user.notifications.remove(notification)
    #     try:
    #         db.session.commit()
    #     except:
    #         db.session.rollback()
    return render_template('home.html',
                            recommended_tabs=recommended_tabs,
                            top_tabs=trending_tabs,
                            user_tabs=user_tabs,
                            user_project_count=len(user_projects),
                            current_user=current_user,
                            project_application=project_application)
