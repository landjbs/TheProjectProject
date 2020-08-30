''' Ranking algorithms for project recommendations '''

import numpy as np
from operator import itemgetter
from datetime import datetime
from sqlalchemy import desc, func
from sqlalchemy.sql.expression import case

from app.project.models import Project
from app.recommendations.utils import get_normed_user_subjects

from time import time


global TIME_BREAKDOWN
TIME_BREAKDOWN = {
    'subjects':0, 'active':0, 'tasks':0, 'timesince':0, 'members':0, 'ids':0
}


def score_project(project, user_subjects):
    ''' Assigns project ranking given user [0,8] '''
    # subject scoring [0,6]
    s = time()
    score = 0
    project_subjects = set(project.subjects)
    for subject, subject_score in user_subjects.items():
        if subject in project_subjects:
            score += subject_score
    score /= (len(user_subjects)+0.0000001)
    score *= 6
    TIME_BREAKDOWN['subjects'] += (time() - s)
    s = time()
    # recently active scoring [0,2]
    if project.recently_active():
        score += 2
    TIME_BREAKDOWN['active'] += (time() - s)
    s = time()
    # tasks scores [0,2] gives boost to projects with incomplete tasks
    n_incomplete = project.tasks.filter_by(complete=False).count()
    if n_incomplete==1:
        score += 1
    elif n_incomplete>1 and n_incomplete<3:
        score += 1.5
    elif n_incomplete>=3:
        score += 2
    TIME_BREAKDOWN['tasks'] += (time() - s)
    s = time()
    # time scores [0,1] give boost to newer projects
    time_since = (datetime.utcnow() - project.posted_on).days
    if time_since<1:
        score += 1
    elif time_since<3:
        score += 0.8
    elif time_since<10:
        score += 0.5
    TIME_BREAKDOWN['timesince'] += (time() - s)
    s = time()
    # members score [0,1] gives boost to more empty projects
    n_members = 0
    for m in project.members:
        n_members += 1
    if (project.team_size>0):
        score += (1 - (n_members / (project.team_size+0.0000001)))
    else:
        score = 0
    TIME_BREAKDOWN['members'] += (time() - s)
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
                                  ).order_by(desc(Project.last_active)).limit(300)
    ## format user preferences ##
    user_subjects = get_normed_user_subjects(user, temp=2)
    ## score each candidate ##
    scored_ids = [
        (project.id , score_project(project, user_subjects))
        for project in candidates
    ]
    result_ids = [
        x[0] for x in sorted(scored_ids, key=itemgetter(1), reverse=True)
    ]
    # add ids of invited projects to front of result ids
    result_ids = (invited_projects + result_ids)
    # build case statement for ordered query
    ordering = case(
        {id: index for index, id in enumerate(result_ids)},
        value=Project.id
    )
    # get query from ordered ids
    results = Project.query.filter(
                Project.id.in_(result_ids)
            ).order_by(ordering).all()
    # if len(results)==0:
        # results = [project for project in Project.query.all().limit(30)]
    print(TIME_BREAKDOWN)
    return results


def get_trending_projects():
    return Project.query.order_by(desc(Project.buzz)).limit(9)


def get_user_projects(user):
    return user.projects
