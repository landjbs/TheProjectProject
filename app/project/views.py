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
        edit_form = Edit_Project(request.form)
        edit_application_form = Edit_Project_Application(request.form)
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
    ''' Apply to or join project according to application and open status '''
    project = Project.query.get_or_404(project_id)
    if project.is_member(current_user):
        flash(f'Could not join {project.name} because you are '
               'already a member.')
        return redirect(request.referrer)
    if project.open:
        if not project.requires_application:
            flash(f'You have been added to {project.name}!')
            project.add_member(current_user)
        else:
            form = Project_Application_Form()
            if form.validate_on_submit():
                if project.get_application(current_user) is not None:
                    flash(f'You have already applied to {project.name}!')
                else:
                    project.apply(user=current_user, text=form.response.data)
                    flash(f'Your application to {project.name} been submitted.')
            else:
                flash(f'Invalid application.')
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


@project.route('/project/<int:project_id>/task', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_task(project_id):
    ''' Add task to project '''
    project = Project.query.get_or_404(project_id)
    form = Task_Form()
    if form.validate_on_submit():
        if not project.add_task(text=form.text.data, author=current_user):
            flash('Could not add task.', 'error')
    return redirect(request.referrer)


@project.route('/project/<int:project_id>/comment', methods=['POST'])
@login_required
@limiter.limit('30 per minute')
def add_comment(project_id):
    ''' Add comment to project '''
    project = Project.query.get_or_404(project_id)
    form = Comment_Form(request.form)
    if form.validate_on_submit():
        if not project.add_comment(text=form.text.data, author=current_user):
            flash('Could not add comment.', 'error')
    return redirect(request.referrer)


@project.route('/project/<int:project_id>/<int:comment_id>')
@login_required
def delete_comment(project_id, comment_id):
    ''' Delete comment from project '''
    project = Project.query.get_or_404(project_id)
    if not project.delete_comment(comment_id=comment_id, user=current_user):
        flash('Cannot delete comment.')
    return redirect(request.referrer)


@project.route('/mark_complete/<int:project_id>/<int:task_id>/<action>')
@login_required
@limiter.limit('5 per minute')
def change_task_status(project_id, task_id, action):
    ''' Mark task as complete, delete task, or remove help '''
    project = Project.query.get_or_404(project_id)
    if not project.change_task_status(task_id, current_user, action):
        flash('Could not update task.')
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



@project.route('/change_project_status/<int:project_id>/<int:user_id>/<action>')
@login_required
@limiter.limit('20/minute')
def change_user_status(project_id, user_id, action):
    ''' Change status of user with repsect to project '''
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    error_flag = False
    ## ACCEPT ##
    if action=='accept':
        if user in project.members:
            flash('Cannot accept user already in project.')
            error_flag = True
        else:
            manager.add_user_to_project(user, project)
    ## REJECT ##
    elif action=='reject':
        # remove user from project
        if user in project.members:
            manager.remove_user_from_project(user, project, admin=True)
        # remove user from pending
        else:
            error_flag = (not manager.reject_user_from_pending(user, project, admin=True))
    ## MAKE OWNER ##
    elif action=='make_owner':
        error_flag = (not transfer_ownership(project, user))
    else:
        flash('Invalid action.')
        error_flag = True
    if not error_flag:
        project.update_last_active()
        db.session.commit()
        db.session.close()
    return redirect(request.referrer)

@project.route('/remove_member/<int:project_id>/<int:user_id>')
@limiter.limit('30/minute')
def remove_member(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Must be project owner to remove member.')
    else:
        if not project.remove_member(user_id=user_id, by_owner=True):
            flash('Could not remove user.', 'error')
        flash(f'User removed from {project.name}.')
    return redirect(request.referrer)


@project.route('/make_owner/<int:project_id>/<int:user_id>')
@limiter.limit('30/minute')
def make_owner(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Must be project owner to transfer ownership.')
    else:
        if not project.transfer_ownership(user_id):
            flash('Could not transfer ownership', 'error')

def reject_application():
    pass


def accept_application():
    pass


@project.route('/complete_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('3 per minute')
def complete_project(project_id):
    ''' Mark project as complete '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can mark a project as complete.')
    else:
        project.update_last_active()
        manager.complete_project(project)
    return redirect(request.referrer)


@project.route('/uncomplete_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('3 per minute')
def uncomplete_project(project_id):
    ''' Mark project as not complete '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can mark a project as incomplete.')
    else:
        project.update_last_active()
        manager.uncomplete_project(project)
    return redirect(request.referrer)


@project.route('/change_project_open/<int:project_id>/<action>', methods=['POST'])
@login_required
@limiter.limit('5 per minute')
def change_project_open(project_id, action):
    ''' Change open status of project '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can change join settings.')
    elif action=='open':
        project.update_last_active()
        manager.open_project(project)
    elif action=='close':
        project.update_last_active()
        manager.close_project(project)
    return redirect(request.referrer)


@project.route('/add_application/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_application(project_id):
    ''' Add applicaiton to project '''
    project = Project.query.get_or_404(project_id)
    form = Edit_Project_Application(request.form)
    if current_user!=project.owner:
        flash('Only the owner can change application settings.')
    elif form.validate_on_submit():
        project.update_last_active()
        manager.add_application(project, form.application_question.data)
    else:
        flash(f'Could not add application: {form.errors[0]}.')
    return redirect(request.referrer)


@project.route('/remove_application_requirement/<int:project_id>', methods=['POST'])
@login_required
def remove_application_requirement(project_id):
    ''' Remove application from project '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can change application settings.')
    else:
        project.update_last_active()
        manager.remove_application_requirement(project)
    return redirect(request.referrer)



@project.route('/leave_project/<int:project_id>', methods=['POST'])
@login_required
def leave_project(project_id):
    project = Project.query.get_or_404(project_id)
    # validate that user is member
    if not current_user in project.members:
        flash(f'Cannot leave {project.name} without being a member.')
        return redirect(request.referrer)
    # transfer ownership
    if (current_user==project.owner):
        if (project.members.count()>1):
            new_owner = User.query.get_or_404(request.form.get('new_owner'))
            success = transfer_ownership(project, new_owner)
            if not success:
                flash('Owner transfer unsuccessful.')
                return redirect(request.referrer)
        else:
            user_code = current_user.code
            manager.delete_project(project)
            flash(f'{project.name} deleted.')
            return user_page(user_code)
    manager.remove_user_from_project(current_user, project, admin=False)
    flash(f'You have left {project.name}.')
    return redirect(request.referrer)
