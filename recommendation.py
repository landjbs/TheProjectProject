'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def recommend_projects(user):
    user_projects = user.projects
    return Project.query.filter(~Project.id.in_(user_projects))
