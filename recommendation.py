'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

import numpy as np
from operator import itemgetter

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def get_normed_user_subjects(user, temp):
    # sum raw counts of user subjects
    norm_sum = 0
    for s in user.subjects:
        norm_sum += np.exp(s.number/temp)
    user_subjects = {s.subject : (np.exp(s.number/temp) / norm_sum)
                    for s in user.subjects}
    return user_subjects


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
    print(f'{project.name}: {score}')
    return score


def recommend_projects(user):
    ## get initial candidates ##
    user_projects = [p.id for p in user.projects]
    candidates = Project.query.filter(Project.open==True,
                                      Project.complete==False,
                                      ~Project.id.in_(user_projects))
    ## format user preferences ##
    user_subjects = get_normed_user_subjects(user, temp=2)
    ## score each candidate ##
    results = [(project,score_project(project, user_subjects)) for project in candidates]
    results = [x[0] for x in sorted(results, key=itemgetter(1), reverse=True)]
    return results
    # return Project.query.filter(~Project.in_(Project.query.filter(user in )))


def recommend_users(project):
    project_members = [u.id for u in project.members]
    project_pending = [a.user.id for a in project.pending]
    project_invitations = [u.id for u in project.invitations]
    return User.query.filter(~User.id.in_(project_members),
                             ~User.id.in_(project_pending),
                             ~User.id.in_(project_invitations))
