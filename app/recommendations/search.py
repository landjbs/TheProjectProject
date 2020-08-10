from app.user.models import User
from app.project.models import Project
from app.subject.models import Subject

from app.utils import partition_query

# TODO: replace with better elastic_search

def text_search(search_text, partition=True):
    ## results ##
    project_results = Project.query.filter(Project.name.contains(search_text) |
                                   Project.oneliner.contains(search_text))
    user_results = User.query.filter(User.name.contains(search_text) |
                                     User.about.contains(search_text))
    subject_results = Subject.query.filter(Subject.name.contains(search_text))
    ## partition ##
    if partition:
        project_results = partition_query(project_results)
        user_results = partition_query(user_results)
        subject_results = partition_query(subject_results)
    ## analytics ##
    project_count = project_results.count()
    user_count = user_results.count()
    subject_count = subject_results.count()
    ## limits ##
    project_results = project_results.limit(30)
    user_results = user_results.limit(30)
    ## return dict of results and analytics
    return {'project'       :   (list(project_results), project_count),
            'user'          :   (list(user_results), user_count),
            'subject'       :   (list(subject_results), subject_count)}
