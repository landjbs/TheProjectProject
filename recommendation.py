'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from operator import itemgetter

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


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
    # sum raw counts of user subjects
    subject_sum = 0
    for s in user.subjects:
        subject_sum += s.number
    # get normalized subject counts
    user_subjects = {s.subject : (s.number/subject_sum)
                    for s in user.subjects}
    ## score each candidate ##
    results = [(project,score_project(project, user_subjects)) for project in candidates]
    results = [x[0] for x in sorted(results, key=itemgetter(1), reverse=True)]
    print(results)
    return results
    # return Project.query.filter(~Project.in_(Project.query.filter(user in )))
