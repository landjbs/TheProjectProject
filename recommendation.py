'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def recommend_projects(user):
    Project.query.filter(Project.owner!=user,
                         not Project.id.in_(user.projects))
