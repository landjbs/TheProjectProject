from flask import (current_app, request, redirect, url_for,
                   render_template, flash, g)
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

# searchables
from app.user.models import User
from app.project.models import Project
from app.subject.models import Subject



def home():
    # recommended projects
    recommended_projects = get_recommended_projects(current_user)
    recommended_tabs = list(partition_query(recommended_projects))
    # top projects
    trending_projects = get_trending_projects()
    trending_tabs =  list(partition_query(trending_projects))
    # user projects
    user_projects = list(get_user_projects(current_user))
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
                            user_project_count=len(user_projects),
                            project_application=project_application)


@hub.route('/home')
@login_required
@mobilized(home)
def home():
    ''' Mobile optimized route for home page '''
    # only load recommended projects and dont tab
    recommended_projects = get_recommended_projects(current_user)
    # get forms
    project_application = Project_Application_Form()
    return render_template('home_mobile.html',
                           recommended_projects=recommended_projects,
                           project_application=project_application)


### SEARCH ###
@hub.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('hub.home'))

    page = request.args.get('page', 1, type=int)

    results = {}
    projects, n_projects = Project.search(g.search_form.search.data, page, 30)
    users, n_users = User.search(g.search_form.search.data, page, 30)
    subjects, n_subjects = Subject.search(g.search_form.search.data, page, 30)

    results = {'project' :   (list(partition_query(projects)), n_projects),
            'user'       :   (list(partition_query(users)), n_users),
            'subject'    :   (list(partition_query(subjects)), n_subjects)}

    project_application = Project_Application_Form()
    return render_template('search.html',
                           results=results,
                           project_application=project_application)

# def search():
#     search_text = request.form.get('search')
#     results = text_search(search_text)
#     # forms
#     project_application = Project_Application_Form()
#     return render_template('search.html',
#                         results=results,
#                         project_application=project_application)
#
#
# ### SEARCH ###
# @hub.route('/search', methods=['GET', 'POST'])
# @mobilized(search)
# @login_required
# @limiter.limit('60 per minute')
# def search_mobile():
#     ''' Mobile optimized search page '''
#     if request.method=='GET':
#         return redirect(url_for('hub.home'))
#     search_text = request.form.get('search')
#     results = text_search(search_text, partition=False)
#     project_application = Project_Application_Form()
#     return render_template('search_mobile.html',
#                         results=results,
#                         project_application=project_application)
