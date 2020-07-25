'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def recommend_projects(user):
    user_projects = Project.query.filter(user in Project.members)
    print(user_projects)
    # return Project.query.filter(~Project.in_(Project.query.filter(user in )))
