'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from operator import itemgetter

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def score_project(user, project):
    ''' Assigns project ranking '''




def recommend_projects(user):
    ## get initial candidates ##
    user_projects = [p.id for p in user.projects]
    candidates = Project.query.filter(Project.open==True,
                                      Project.complete==False,
                                      ~Project.id.in_(user_projects))
    ## format user preferences ##
    # sum raw counts of user subjects
    subject_sum = 0
    for s in user.subjects:
        subject_sum += s.number
    # get normalized subject counts
    user_subjects = {s.subject : (s.number/subject_sum)
                    for s in user.subjects}
    #
    user_subjects = {}
    ## score each candidate ##
    return candidates
    # return Project.query.filter(~Project.in_(Project.query.filter(user in )))
