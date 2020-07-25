'''
Ranking, sorting, and searching algorithms for projects, users, and subjects.
'''

from application.models import User, Project, Subject


PROJECT_LIMIT = 30


def recommend_projects(user):
    # get all open and not completed projects of which user is member
    user_projects = [p.id for p in user.projects]
    user_projects = Project.query.filter(Project.open==True,
                                         Project.complete==False,
                                         ~Project.id.in_(user_projects))
    return user_projects
    # return Project.query.filter(~Project.in_(Project.query.filter(user in )))
