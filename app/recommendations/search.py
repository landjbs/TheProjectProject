from app.user.models import User
from app.project.models import Project
from app.subject.models import Subject

from app.utils import partition_query

# TODO: replace with better elastic_search

def text_search(search_text):
    ## results ##
    project_results = Project.query.filter(
        Project.name.contains(search_text) |
        Project.oneliner.contains(search_text)
    )
    user_results = User.query.filter(
        User.name.contains(search_text) |
        User.about.contains(search_text)
    )
    subject_results = Subject.query.filter(
        Subject.name.contains(search_text)
    )
    company_results = Company.query.filter(
        Company.name.contains(search_text) |
        Company.oneliner.contains(search_text)
    )
    ## analytics ##
    project_count = project_results.count()
    user_count = user_results.count()
    subject_count = subject_results.count()
    company_count = company_results.count()
    ## limits ##
    project_results = project_results.limit(30)
    user_results = user_results.limit(30)
    company_results = company_results.limit(30)
    ## return dict of results and analytics
    return {
        'project'       :   (project_results.all(),     project_count),
        'user'          :   (user_results.all(),        user_count),
        'subject'       :   (subject_results.all(),     subject_count),
        'company'       :   (company_results.all(),     company_count)
    }
