from flask import (current_app, request, redirect, url_for,
                   render_template, flash, g, make_response)
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


@hub.route('/home')
@login_required
def home():
    # recommended
    recommended = get_recommended_projects(current_user)
    # show trending and owned only on desktop
    trending, my = (get_trending_projects().all(),
                    get_user_projects(current_user).all()) \
            if not request.MOBILE else (None, None)
    return render_template(
        'home.html', recommended=recommended, trending=trending, my=my
    )


@hub.route('/load_recommendations')
def load_recommendations():
    # recommended
    recommended = get_recommended_projects(current_user)
    if request.args:
        # get counter from query string
        counter = int(request.args.get("c"))
        if counter == 0:
            # [0:quantity] from recommendations
            res = make_response(jsonify(db[0: quantity]), 200)
        elif counter == posts:
            # no posts left
            res = make_response(jsonify({}), 200)
        else:
            print(f"Returning posts {counter} to {counter + quantity}")
            # Slice counter -> quantity from the db
            res = make_response(jsonify(db[counter: counter + quantity]), 200)




### SEARCH ###
# @hub.route('/search')
# @login_required
# def search():
#     if not g.search_form.validate():
#         return redirect(url_for('hub.home'))
#
#     page = request.args.get('page', 1, type=int)
#
#     results = {}
#     projects, n_projects = Project.search(g.search_form.search.data, page, 30)
#     users, n_users = User.search(g.search_form.search.data, page, 30)
#     subjects, n_subjects = Subject.search(g.search_form.search.data, page, 30)
#
#     results = {'project' :   (list(partition_query(projects)), n_projects),
#             'user'       :   (list(partition_query(users)), n_users),
#             'subject'    :   (list(partition_query(subjects)), n_subjects)}
#
#     project_application = Project_Application_Form()
#     return render_template('search.html',
#                            results=results,
#                            project_application=project_application)


@hub.route('/search', methods=['GET', 'POST'])
@login_required
@limiter.limit('60 per minute')
def search():
    if not g.search_form.validate():
        return redirect(url_for('hub.home'))
    search_text = g.search_form.search.data
    results = text_search(search_text)
    return render_template('search.html',
                        results=results,
                        search_text=search_text)
