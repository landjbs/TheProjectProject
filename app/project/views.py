from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query
# package imports
from .models import Project
from .forms import CommentForm, Task_Form, Project_Application_Form


@application.route('/project=<project_code>', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def project_page(project_code):
    project = Project.query.filter_by(code=project_code).first_or_404()
    # forms
    comment_form = Comment_Form(request.form)
    task_form = Task_Form(request.form)
    project_application = Project_Application_Form(request.form)
    ## task data visualization ##
    # vis activity
    activity_data = {} if project.tasks.count()>0 else False
    if activity_data != False:
        start_activity, end_activity, earliest = tasks_to_daily_activity(project.tasks)
        activity_data['start_activity'] = start_activity
        activity_data['end_activity'] = end_activity
        activity_data['earliest'] = earliest
    # compile counts of tasks completed by each worker
    authors, completers = [], []
    for task in project.tasks:
        authors.append(task.author)
        if task.complete:
            for worker in task.workers:
                completers.append(worker)
    # select top 5 to plot
    author_counts = Counter(authors)
    completed_counts = Counter(completers)
    authored, completed = {}, {}
    # all people related to project tasks
    for n in set(completed_counts.keys()).union(set(author_counts.keys())):
        # get number of authored and completed tasks
        user_author_count = author_counts.get(n)
        user_completed_count = completed_counts.get(n)
        authored[n] = user_author_count if user_author_count else 0
        completed[n] = user_completed_count if user_completed_count else 0
    ## subject visualization ##
    project_subjects = {s.name:0 for s in project.subjects}
    if project_subjects!={}:
        for member in project.members:
            for user_subject in member.subjects:
                name = user_subject.subject.name
                if name in project_subjects:
                    # -1 to account for skills gained via project association
                    project_subjects[name] += (user_subject.number)
    ## recommended members ##
    recommended_tabs = False
    edit_form = False
    edit_application_form = False
    show_edit_modal = False
    if current_user==project.owner:
        if project.open and not project.complete:
            recommended_members = rec.recommend_users(project)
            recommended_tabs = list(partition_query(recommended_members))
        ## edit project form ##
        edit_form = forms.Edit_Project(request.form)
        edit_application_form = forms.Edit_Project_Application(request.form)
        if request.method=='POST':
            if edit_form.validate_on_submit():
                edits_made = False
                # name
                new_name = edit_form.name.data
                if new_name!=project.name:
                    project.name = new_name
                    edits_made = True
                # oneliner
                new_oneliner = edit_form.oneliner.data
                if new_oneliner!=project.oneliner:
                    project.oneliner = new_oneliner
                    edits_made = True
                # summary
                new_summary = edit_form.summary.data
                if new_summary!=project.summary:
                    project.summary = new_summary
                    edits_made = True
                # estimated time
                new_time = edit_form.estimated_time.data
                if new_time!=project.estimated_time:
                    project.estimated_time = new_time
                    edits_made = True
                # team size
                new_size = edit_form.team_size.data
                if new_size!=project.team_size:
                    project.team_size = new_size
                    edits_made = True
                if edits_made:
                    flash(f'You have successfully edited {project.name}.')
                    db.session.add(project)
                    db.session.commit()
                    db.session.close()
            else:
                show_edit_modal = True
    return render_template('project.html', project=project,
                            comment_form=comment_form,
                            project_application=project_application,
                            task_form=task_form,
                            activity_data=activity_data,
                            authored=authored,
                            completed=completed,
                            project_subjects=project_subjects,
                            recommended_tabs=recommended_tabs,
                            edit_form=edit_form,
                            edit_application_form=edit_application_form)
