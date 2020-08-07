from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query
from app.project.forms import Project_Application_Form
# package imports
from .models import User
from .forms import Edit_User
from ..user import user


@user.route('/user=<code>', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def user_page(code):
    user = User.query.filter_by(code=code).first_or_404()
    # worked tasks
    tasks = user.tasks_worked
    task_data = {} if (len(tasks)>0) else None
    if task_data is not None:
        _, end_activity, earliest = tasks_to_daily_activity(tasks)
        task_data['end_activity'] = end_activity
        task_data['earliest'] = earliest
    # owned projects
    owned = user.owned
    owned_tabs = list(partition_query(owned))
    # member projects
    member_projects = [project for project in user.projects
                       if not project in owned]
    member_tabs = list(partition_query(member_projects))
    # subjects
    subject_data = user.subject_data()
    ## forms ##
    # application to projects
    project_application = Project_Application_Form()
    # edit user account
    show_edit_modal = False
    edit_form = Edit_User() if (current_user==user) else False
    if request.method=='POST':
        if edit_form.validate_on_submit():
            edits_made = False
            # name
            new_name = edit_form.name.data
            if new_name!=user.name:
                user.name = new_name
                edits_made = True
            # url
            new_url = edit_form.url.data
            if new_url!=user.url:
                user.url = new_url
                edits_made = True
            # about
            new_about = edit_form.about.data
            if new_about!=user.about:
                user.about = new_about
                edits_made = True
            # new password
            if edit_form.password.data!='':
                if not user.check_password(edit_form.password.data):
                    user.set_password(edit_form.password.data)
                    edits_made = True
            if edits_made:
                flash('You have successfully edited your acount.')
                user.update()
        else:
            show_edit_modal = True
    return render_template('user.html',
                            user=user,
                            task_data=task_data,
                            subject_data=subject_data,
                            owned_tabs=owned_tabs,
                            member_tabs=member_tabs,
                            project_application=project_application,
                            edit_form=edit_form,
                            show_edit_modal=show_edit_modal)


## user to self interactions ##
@user.route('/flash_encouragement', methods=['POST'])
def flash_encouragement():
    flash('Reminder: You are awesome and will do amazing '
         'things if you believe in yourself.')
    return redirect(request.referrer)


@user.route('/delete_user', methods=['POST'])
@login_required
@limiter.limit('2 per minute')
def delete_user():
    for project in current_user.owned:
        if len(project.members.all())>1:
            new_owner = User.query.get_or_404(request.form.get(f'new_owner_{project.id}'))
            success = transfer_ownership(project, new_owner)
            if not success:
                flash(f'Owner transfer unsuccessful of {project.name}.')
                return redirect(request.referrer)
        else:
            project.delete()
    current_user.delete()
    flash('Your account has been deleted. We are sorry to see you go!')
    return redirect(url_for('base.index'))


## user to user interactions ##
@user.route('/report_user/<int:target_user_id>', methods=['POST'])
@login_required
@limiter.limit('2 per minute')
def report_user(target_user_id):
    target_user = User.query.get_or_404(int(target_user_id))
    text = request.form.get('report_text')
    if target_user is None:
        flash('User does not exist.')
    elif target_user==current_user:
        flash('You cannot report yourself.')
    elif not target_user.accepted:
        flash('Cannot report user, as they are still pending acceptance.')
    else:
        flash(f'You have reported {target_user.name}. We are so sorry you have '
            'experienced issues while using our platform and will begin '
            'reviewing your report immediately. If necessary, we may contact '
            'you for more information.')
        manager.report_user(current_user, target_user, text=text)
    return redirect(request.referrer)


@user.route('/collaborate/<int:target_user_id>', methods=['POST'])
@login_required
@limiter.limit('10/minute; 100/hour')
def collaborate(target_user_id):
    error_flag = False
    project = Project.query.get_or_404(request.form.get('selected_project'))
    target_user = User.query.get_or_404(target_user_id)
    if not current_user==project.owner:
        flash('Cannot invite collaborator to project you do not own.')
    elif current_user==target_user:
        flash("You don't need to send an invitation to collaborate with "
              "yourself!")
    elif not target_user.accepted:
        flash(f'{target_user.name} user has not been accepted to TheProjectProject yet.')
    elif target_user in project.members:
        flash(f'{target_user.name} is already a member of {project.name}.')
    elif target_user.has_applied(project):
        flash(f'{target_user.name} has already applied to {project.name}. '
            'Go to the project page to accept their application.')
    elif target_user in project.invitations:
        flash(f'You have already invited {target_user.name} to join '
              f'{project.name}. You will be notified when they respond.')
    else:
        target_user.invitations.append(project)
        notifcation = Notification(text=f'{current_user.name} has invited you '
                                        f'to collaborate on {project.name}! '
                                        'Visit your profile page to reply.')
        target_user.notifications.append(notifcation)
        flash(f'You have sent {target_user.name} an invitation to collaborate '
              f'on {project.name}. You will be notified when they respond.')
        project.update_last_active()
        db.session.commit()
        db.session.close()
    return redirect(request.referrer)
