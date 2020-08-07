from app.user.models import User
from app.project.models import Project
from app.subject.models import Subject


# TODO: replace with better elastic_search

def text_search(search_text):
    # project results
    project_results = Project.query.filter(Project.name.contains(search_text) |
                                   Project.oneliner.contains(search_text))
    project_tabs = list(partition_query(project_results.limit(30)))
    # user results
    user_results = User.query.filter(User.name.contains(search_text) |
                                     User.about.contains(search_text))
    user_tabs = list(partition_query(user_results.limit(30)))
    # subject results
    subject_results = Subject.query.filter(Subject.name.contains(search_text))
    subject_tabs = list(partition_query(subject_results.limit(30)))
    return (project_tabs, user_tabs, subject_tabs)
