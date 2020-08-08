''' Ranking algorithms for user recommendations '''

import numpy as np
from operator import itemgetter
from datetime import datetime
from sqlalchemy import desc

from app.user.models import User
from app.recommendations.utils import get_normed_user_subjects


def score_user(user, project):
    score = 0
    # subject scores [0, 3]
    user_subjects = get_normed_user_subjects(user, temp=2)
    for subject in project.subjects:
        if subject in user_subjects:
            score += user_subjects[subject]
    score *= 3
    # tasks completed [0, 2] ratio of tasks completed to projects
    n_tasks = 0
    n_user_completed = 0
    n_worked_with = 0
    for project in user.projects:
        for task in project.tasks:
            n_tasks += 1
            if user in task.workers:
                n_user_completed += 1
    if n_tasks>0:
        score += ((2 * n_user_completed) / n_tasks)
    else:
        # new users given better score than veteran with <15% task completions
        score += 0.15
    if user.is_active():
        score += 2
    elif user.last_active is None:
        pass
    else:
        time_since = (datetime.utcnow() - user.last_active).days
        if time_since < 2:
            score += 1
        elif time_since < 4:
            score += 0.5
        elif time_since < 10:
            score += 0.2
    return score


def recommend_users(project):
    ## get initial candidates ##
    project_members = [u.id for u in project.members]
    project_pending = [a.user.id for a in project.pending]
    project_invitations = [u.id for u in project.invitations]
    project_rejections = [u.id for u in project.rejections]
    nowshow_ids = (project_members + project_pending
                  + project_invitations + project_rejections)
    candidates = User.query.filter(~User.id.in_(nowshow_ids),
                                   User.accepted==True,
                                   User.admin==False
                                    ).limit(200)
    ## rank candidates ##
    results = [(user, score_user(user, project)) for user in candidates]
    results = [x[0] for x in sorted(results, key=itemgetter(1)[:15], reverse=True)]
    return results
