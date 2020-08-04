'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

import numpy as np
from operator import itemgetter

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
    ''' Assigns project ranking given user '''
    # sum raw subject counts across project users
    # for member in project.members:
    #     for s in member.subjects:
    #         if s.subject in project.subjects:
    #             user_sum += s.number
    # project_subjects = {subject:(1-) for subject in}
    score = 0
    for subject, subject_score in user_subjects.items():
        if subject in project.subjects:
            score += subject_score
    return score


def score_user(user, project_subjects):
    score = 0
    # for subject, subject_score in project_subjects.items():



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
                                      ~Project.id.in_(nowshow_ids)).limit(200)
    ## get invited projects ##
    invited = [project for project in user.invitations]
    ## format user preferences ##
    user_subjects = get_normed_user_subjects(user, temp=2)
    ## score each candidate ##
    results = [(project,score_project(project, user_subjects)) for project in candidates]
    results = [x[0] for x in sorted(results, key=itemgetter(1), reverse=True)]
    results = (invited + results)
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
    project_subjects = get_normed_project_subjects(project, temp=3)
    results = [(user, score_user(user, project_subjects))
                for user in candidates]
    return candidates


def user_project(user):
    pass
