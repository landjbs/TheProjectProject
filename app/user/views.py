from flask import request, redirect, url_for, render_template, flash, g
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query
from app.project.models import Project
from app.subject.models import Subject
# package imports
from .models import User
from .forms import Edit_User
from ..user import user


@user.route('/user=<code>', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
def user_page(code):
    user = User.query.filter_by(code=code).first_or_404()
    g.user = user
    # user data
    task_data = False
    subject_data = False
    # worked tasks
    tasks = user.tasks_worked
    task_data = {} if (len(tasks)>0) else None
    if task_data is not None:
        _, end_activity, earliest = tasks_to_daily_activity(tasks)
        task_data['end_activity'] = end_activity
        task_data['earliest'] = earliest
    # owned projects
    owned = user.owned.all()
    # member projects
    member = [project for project in user.projects if not project in owned]
    # subjects
    subject_data = user.subject_data()
    ## forms ##
    # edit user account
    show_edit_modal = False
    edit_form = False
    if current_user==user:
        edit_form = Edit_User()
        # edit_form.subjects.choices = [(s.id, s.name) for s in Subject.query.all()]
        # set defaults
        # edit_form.name.default = user.name
        # # edit_form.about.default = user.about
        # # edit_form.password.default = ""
        # # edit_form.confirm.default = ""
        # edit_form.subjects.default = [s.subject.id for s in user.selected_subjects()]
    if request.method=='POST':
        if edit_form.validate_on_submit():
            edits_made = False
            # name
            new_name = edit_form.name.data
            if new_name!=user.name:
                user.name = new_name
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
    return render_template('user.html' if not request.MOBILE else 'user_mobile.html',
                            user=user,
                            task_data=task_data,
                            subject_data=subject_data,
                            owned=owned,
                            member=member,
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
            success = project.make_owner(new_owner)
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
# @limiter.limit('5/minute')
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
        target_user.report(text=text, reporter=current_user)
    return redirect(request.referrer)


## collaboration ##
@user.route('/collaborate/<int:target_user_id>', methods=['POST'])
@login_required
@limiter.limit('10/minute; 100/hour')
def collaborate(target_user_id):
    error_flag = False
    project = Project.query.get_or_404(request.form.get('selected_project'))
    target_user = User.query.get_or_404(target_user_id)
    message, category = target_user.collaborate(project, current_user)
    flash(message, category)
    return redirect(request.referrer)


@user.route('/accept_collaboration/<int:project_id>')
@login_required
@limiter.limit('60 per minute')
def accept_collaboration(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user in project.invitations:
        flash(f'You have accepted the invitation to {project.name}.', 'success')
        project.add_member(current_user, notify_owner=True)
        return redirect(url_for('project.project_page',
                                project_code=project.code))
    else:
        flash(f'Could not join {current_user.name} as you have not been invited.',
               'error')
    return redirect(request.referrer)


@user.route('/reject_collaboration/<int:project_id>')
@login_required
def reject_collaboration(project_id):
    project = Project.query.get_or_404(project_id)
    message, category = current_user.reject_collaboration(project)
    flash(message, category)
    return redirect(request.referrer)


@user.route('/withdraw_collaboration/<int:user_id>/<int:project_id>')
@login_required
def withdraw_collaboration(user_id, project_id):
    user = User.query.get_or_404(user_id)
    project = Project.query.get_or_404(project_id)
    if not current_user==project.owner:
        flash('Only the project owner can withdraw collaborations.', 'error')
    else:
        message, category = user.withdraw_collaboration(project)
        flash(message, category)
    return redirect(request.referrer)


## avaliability ##
@user.route('/mark_available')
@login_required
def mark_available():
    if current_user.mark_available():
        flash(('You have marked yourself as available: you will now be '
            'recommend to project owners!'))
    else:
        flash('Could not change status to available.')
    return redirect(request.referrer)


@user.route('/mark_unavailable')
@login_required
def mark_unavailable():
    if current_user.mark_unavailable():
        flash(('You have marked yourself as unavailable: you will not be '
        'recommended to project owners until you change your status back'
        'to available.'))
    else:
        flash('Could not change status to unavailable.')
    return redirect(request.referrer)
