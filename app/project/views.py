from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from collections import Counter # # TEMP: COUNTER SHOULD BE MOVED OR REPLACED
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query
# package imports
from .models import Project
from .forms import Comment_Form, Task_Form, Project_Application_Form
from ..project import project


@project.route('/project=<project_code>', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def project_page(project_code):
    project = Project.query.filter_by(code=project_code).first_or_404()
    # forms
    comment_form = Comment_Form()
    task_form = Task_Form()
    project_application = Project_Application_Form()
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
    project_subjects = project.subject_data()

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


## user to project interactions ##
@project.route('/join_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('5 per minute')
def join_project(project_id):
    ''' Join project according to application and open status'''
    raise ValueError('not reconfigured!')
    project = Project.query.get_or_404(project_id)
    if is_project_member(current_user, project):
        flash(f'Could not join {project.name} because you are '
                'already a member.')
        return redirect(request.referrer)
    if project.open:
        if not project.requires_application:
            flash(f'You have been added to {project.name}!')
            manager.add_user_to_project(current_user, project)
        else:
            form = forms.Project_Application_Form(request.form)
            if form.validate_on_submit():
                application = project.pending.filter_by(user=current_user).first()
                if application is not None:
                    flash(f'You have already applied to {project.name}!')
                else:
                    application = Project_Application(project=project,
                                                    user=current_user,
                                                    text=form.response.data)
                    project.pending.append(application)
                    flash(f'Your application to {project.name} been submitted.')
                    # notify project owner
                    notification = Notification(text=f'{current_user.name} has '
                                                     f'applied to {project.name}.')
                    project.owner.notifications.append(notification)
            else:
                flash(f'Invalid application.')
        db.session.add(project)
        db.session.commit()
        db.session.close()
    else:
        flash('The project owner has closed this project.')
    return redirect(request.referrer)


@project.route('/like/<int:project_id>/<action>')
@login_required
@limiter.limit('45 per minute')
def like_action(project_id, action):
    ''' Star or unstar project '''
    project = Project.query.get_or_404(project_id)
    if action == 'like':
        current_user.star_project(project)
    if action == 'unlike':
        current_user.unstar_project(project)
    return redirect(request.referrer)



@application.route('/project/<int:project_id>/task', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_task(project_id):
    ''' Add task to project '''
    project = Project.query.get_or_404(project_id)
    if not is_project_member(current_user, project):
        return redirect(request.referrer)
    form = forms.Task_Form(request.form)
    if form.validate_on_submit():
        task = Task(text=form.text.data, author=current_user)
        manager.add_task(project, current_user, task)
    return redirect(request.referrer)


@application.route('/project/<int:project_id>/comment', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_comment(project_id):
    ''' Add comment to project '''
    project = Project.query.get_or_404(project_id)
    form = forms.Comment_Form(request.form)
    if form.validate_on_submit():
        comment = Comment(text=form.text.data, author=current_user)
        manager.add_comment(project=project, user=current_user, comment=comment)
    return redirect(request.referrer)


@application.route('/project/<int:project_id>/<int:comment_id>')
@login_required
def delete_comment(project_id, comment_id):
    ''' Delete comment from project '''
    project = Project.query.get_or_404(project_id)
    comment = Comment.query.get_or_404(comment_id)
    if current_user in [project.owner, comment.author]:
        db.session.delete(comment)
        db.session.commit()
        db.session.close()
    else:
        flash('Cannot delete comment.')
    return redirect(request.referrer)


@application.route('/mark_complete/<int:project_id>/<int:task_id>/<action>')
@login_required
@limiter.limit('5 per minute')
def mark_task_complete(project_id, task_id, action):
    ''' Mark task as complete, delete task, or remove help '''
    raise ValueError('Move most of functionality to task class')
    project = Project.query.get_or_404(project_id)
    # screen non-members
    if not is_project_member(current_user, project):
        return redirect(request.referrer)
    # get task
    task = Task.query.get_or_404(task_id)
    if (action=='complete'):
        if not task.complete:
            task.mark_complete(current_user)
        else:
            task.add_worker(current_user)
    elif (action=='back'):
        if current_user in task.workers:
            task.workers.remove(current_user)
        if (len(task.workers)==0):
            task.mark_incomplete()
    elif (action=='delete'):
        if (current_user==task.author):
            db.session.delete(task)
    project.update_last_active()
    db.session.commit()
    db.session.close()
    return redirect(request.referrer)


## owner to project actions ##
def transfer_ownership(project, user):
    ''' Transfer ownership of project from current_user to user '''
    raise ValueError('Move to project class')
    if current_user!=project.owner:
        flash('Only the owner can transfer project ownership.')
        return False
    if user==project.owner:
        flash(f'{user.name} is already the project owner.')
        return False
    if not user in project.members:
        flash('Cannot make non-member a project owner.')
        return False
    # notifications
    project.update_last_active()
    notification = Notification(text=f'{project.owner.name} has '
            f'transferred ownership of {project.name} to {user.name}.')
    for member in project.members:
        if not member in [user, current_user]:
            member.notifications.append(notification)
    project.owner = user
    notification = Notification(text='You have been promoted to owner '
                                     f'of {project.name}!')
    user.notifications.append(notification)
    flash(f'You have transferred ownership of {project.name} to '
          f'{user.name}.')
    return True
