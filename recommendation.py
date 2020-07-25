'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def recommend_projects(user):
    return Project.query.filter(Project.owner!=user,
                                ~Project.id.in_(user.projects))
