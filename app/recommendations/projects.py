''' Ranking algorithms for project recommendations '''

import numpy as np
from operator import itemgetter
from datetime import datetime
from sqlalchemy import desc, func, or_
from sqlalchemy.sql.expression import case

from app.project.models import Project
from app.recommendations.utils import get_normed_user_subjects


RESULT_NUM = 30


def score_project(project, user_subjects):
    ''' Assigns project ranking given user [0,8] '''
    # subject scoring [0,6]
    score = 0
    project_subjects = set(project.subjects)
    for subject, subject_score in user_subjects.items():
        if subject in project_subjects:
            score += subject_score
    score /= (len(user_subjects)+0.0000001)
    score *= 6
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
    if (project.team_size>0):
        score += (1 - (n_members / (project.team_size+0.0000001)))
    else:
        score = 0
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
    # add completed and closed projects if results are too few
    n_results = len(result_ids)
    if (n_results < RESULT_NUM):
        # TODO: figure out edge case in closed/completed that allows result ids in
        closed_or_completed = Project.query.filter(
                                        or_(Project.open==False,
                                            Project.complete==False)
                                    ).order_by(desc(Project.last_active)
                                ).limit(RESULT_NUM - n_results)
        result_ids += set(p.id for p in closed_or_completed).difference(set(result_ids + nowshow_ids))
        n_results = len(result_ids)
        if (n_results < RESULT_NUM):
            result_ids += list(nowshow_ids)
    # if past or at max, slice to max
    result_ids = result_ids[:RESULT_NUM]
    # if still nothing, return empty list
    if len(result_ids)==0:
        return []
    # build case statement for ordered query
    # ordering = case(
    #     {id: index for index, id in enumerate(result_ids)},
    #     value=Project.id
    # )
    # get query from ordered ids
    # OPTIMIZE: case result query doesn't work yet, time against get by id and fix if way faster
    results = [Project.get_by_id(id) for id in result_ids]
    # results = Project.query.filter(
                # Project.id.in_(result_ids)
            # ).order_by(ordering).all()
    # if len(results)==0:
        # results = [project for project in Project.query.all().limit(30)]
    return results


def get_trending_projects():
    return Project.query.order_by(desc(Project.buzz)).limit(9)


def get_user_projects(user):
    return user.projects
