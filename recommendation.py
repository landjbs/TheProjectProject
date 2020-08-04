'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

import numpy as np
from operator import itemgetter
from datetime import datetime

from application.models import User, Project, Subject


PROJECT_LIMIT = 30
USER_OWNED_CUTOFF = 5 # max number of active owned projects to be recommended


def get_normed_user_subjects(user, temp):
    # sum raw counts of user subjects
    norm_sum = 0
    for s in user.subjects:
        norm_sum += np.exp(s.number/temp)
    user_subjects = {s.subject : (np.exp(s.number/temp) / norm_sum)
                    for s in user.subjects}
    return user_subjects


def get_normed_project_subjects(project, temp):
    subject_num = project.subjects.count()
    project_subjects = {subject : (1/subject_num)
                        for subject in project.subjects}
    return project_subjects


def score_project(project, user_subjects):
    ''' Assigns project ranking given user [0,8] '''
    # subject scoring [0,4]
    score = 0
    for subject, subject_score in user_subjects.items():
        if subject in project.subjects:
            score += subject_score
    score /= (len(user_subjects) * 0.25)
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
    time_since = (project.posted_on - datetime.utcnow()).days
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
    score += (1 - (n_members / project.team_size))
    return score


def score_user(user, project):
    score = 0
    # subject scores [0, 3]
    user_subjects = get_normed_user_subjects(user, temp=2)
    for subject, subject_score in project_subjects.items():
        if subject in user_subjects:
            score += user_subjects[subject]
    score *= 3
    # tasks completed [0, 2] ratio of tasks completed to projects
    for project in user.projects:
        n_tasks = len(project.tasks)
        print(n_tasks)
    return 1


def recommend_projects(user):
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
                                  ).limit(200)
    ## get invited projects ##
    invited = [project for project in user.invitations]
    ## format user preferences ##
    user_subjects = get_normed_user_subjects(user, temp=2)
    ## score each candidate ##
    results = [(project,score_project(project, user_subjects)) for project in candidates]
    results = [x[0] for x in sorted(results, key=itemgetter(1), reverse=True)]
    results = (invited + results)
    if len(results)==0:
        results = user.projects
    return results


def recommend_users(project):
    ## get initial candidates ##
    project_members = [u.id for u in project.members]
    project_pending = [a.user.id for a in project.pending]
    project_invitations = [u.id for u in project.invitations]
    project_rejections = [u.id for u in project.rejections]
    nowshow_ids = (project_members + project_pending
                  + project_invitations + project_rejections)
    candidates = User.query.filter(~User.id.in_(nowshow_ids))
    ## rank candidates ##
    results = [(user, score_user(user, project)) for user in candidates]
    return candidates


def user_projects(user):
    return user.projects
