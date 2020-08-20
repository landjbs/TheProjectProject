''' Ranking algorithms for project recommendations '''

import numpy as np
from operator import itemgetter
from datetime import datetime
from sqlalchemy import desc

from app.project.models import Project
from app.recommendations.utils import get_normed_user_subjects

def score_project(project, user_subjects):
    ''' Assigns project ranking given user [0,8] '''
    # subject scoring [0,4]
    score = 0
    for subject, subject_score in user_subjects.items():
        if subject in project.subjects:
            score += subject_score
    score /= (len(user_subjects)+0.0000001 * 0.25)
    # recently active scoring [0,2]
    if project.recently_active():
        score += 2
    # tasks scores [0,2] gives boost to projects with incomplete tasks
    n_incomplete = project.tasks.filter_by(complete=False).count()
    if n_incomplete==1:
        score += 1
    elif n_incomplete>1 and n_incomplete<3:
        score += 1.5
    elif n_incomplete>=3:
        score += 2
    # time scores [0,1] give boost to newer projects
    time_since = (datetime.utcnow() - project.posted_on).days
    if time_since<1:
        score += 1
    elif time_since<3:
        score += 0.8
    elif time_since<10:
        score += 0.5
    # members score [0,1] gives boost to more empty projects
    n_members = 0
    for m in project.members:
        n_members += 1
    score += (1 - (n_members / (project.team_size+0.0000001)))
    return score


def get_recommended_projects(user):
    ## get initial candidates ##
    member_projects = [p.id for p in user.projects]
    pending_projects = [p.project.id for p in user.pending]
    invited_projects = [p.id for p in user.invitations]
    rejected_projects = [p.id for p in user.rejections]
    nowshow_ids = (member_projects + pending_projects
                   + invited_projects + rejected_projects)
    candidates = Project.query.filter(Project.open==True,
                                      Project.complete==False,
                                      ~Project.id.in_(nowshow_ids)
                                  ).order_by(desc(Project.last_active)).limit(100)
    ## get invited projects ##
    invited = [project for project in user.invitations]
    ## format user preferences ##
    user_subjects = get_normed_user_subjects(user, temp=2)
    ## score each candidate ##
    results = [(project,score_project(project, user_subjects)) for project in candidates]
    results = [x[0] for x in sorted(results, key=itemgetter(1), reverse=True)]
    results = (invited + results)
    results = results[:30]
    if len(results)==0:
        results = user.projects.all()
    return results


def get_trending_projects():
    return Project.query.order_by(desc(Project.buzz)).limit(9)


def get_user_projects(user):
    return user.projects
