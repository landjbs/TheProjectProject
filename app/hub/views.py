from flask import (current_app, request, redirect, url_for,
                   render_template, flash)
from flask_login import current_user, login_required
from flask_mobility.decorators import mobilized
from datetime import datetime

from ..hub import hub
from app.utils import partition_query
from app.extensions import limiter
from app.recommendations.projects import (get_recommended_projects,
                                    get_trending_projects, get_user_projects)
from app.recommendations.search import text_search
from app.project.forms import Project_Application_Form


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
    project_application = Project_Application_Form()
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
                            user_project_count=user_projects.count(),
                            project_application=project_application)

@hub.route('/home')
@login_required
@mobilized(home)
def home():
    ''' Mobile optimized route for home page '''
    print('MOBILIZED')
    # only load recommended projects and dont tab
    recommended_projects = get_recommended_projects(current_user)
    # get forms
    project_application = Project_Application_Form()
    return render_template('home_mobile.html',
                           recommended_projects=recommended_projects,
                           project_application=project_application)


@hub.route('/search', methods=['GET', 'POST'])
# @mobilized(search)
@login_required
@limiter.limit('60 per minute')
def search():
    if request.method=='GET':
        return redirect(url_for('hub.home'))
    search_text = request.form.get('search')
    project_tabs, user_tabs, subject_tabs = text_search(search_text)
    # forms
    project_application = Project_Application_Form()
    return render_template('search.html',
                        project_tabs=project_tabs,
                        user_tabs=user_tabs,
                        subject_tabs=subject_tabs,
                        search_text=search_text,
                        project_application=project_application)



# def search_mobile():
#     ''' Mobile optimized search page '''
