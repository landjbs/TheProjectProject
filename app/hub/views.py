from flask import (current_app, request, redirect, url_for,
                   render_template, flash, abort)
from flask_login import current_user, login_required
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime

from ..hub import hub
from app.recommendations.projects import recommend_projects


@hub.route('/home', methods=['GET'])
@login_required
def home():
    # recommended projects
    recs = recommend_projects(current_user)
    # recs = db.session.query(Project).limit(30)
    recommended_tabs = list(partition_query(recs))
    # top projects
    tops = db.session.query(Project).order_by(desc(Project.buzz)).limit(9)
    top_tabs =  list(partition_query(tops))
    # user projects
    user_projs = rec.user_projects(current_user)
    user_tabs = list(partition_query(user_projs))
    project_application = forms.Project_Application_Form(request.form)
    # notifcations
    if (current_user.notifications.count())>0:
        for notification in current_user.notifications:
            flash(notification.text)
            current_user.notifications.remove(notification)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return render_template('home.html', recommended_tabs=recommended_tabs,
                            top_tabs=top_tabs, user_tabs=user_tabs,
                            user_project_count=len(user_projs),
                            current_user=current_user,
                            project_application=project_application)
