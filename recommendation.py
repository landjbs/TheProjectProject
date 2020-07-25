'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def recommend_projects(user):
    open_projects = Project.query.filter_by(open=True, complete=False)
    print(open_projects.all())
    # user_projects = Project.query.filter(Project.in_(user.projects))
    # print(user_projects)
    # return Project.query.filter(~Project.in_(Project.query.filter(user in )))
