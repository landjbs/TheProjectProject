from flask import request, redirect, url_for, render_template, flash, jsonify, g, get_template_attribute
from flask_login import login_required, current_user
from flask_mobility.decorators import mobilized
from collections import Counter # # TEMP: COUNTER SHOULD BE MOVED OR REPLACED
# absolute imports
from app.extensions import limiter
from app.utils import tasks_to_daily_activity, partition_query, filter_string
from app.recommendations.users import recommend_users
from app.subject.models import Subject
from app.competition.models import Competition
from app.user.models import User
from app.link.forms import Add_Link
# package imports
from .models import Project
from .forms import (Add_Project, Comment_Form, Task_Form,
                    Project_Application_Form, Edit_Project,
                    Edit_Project_Application)
from ..project import project


@project.route('/new_add', methods=['GET','POST'])
@project.route('/new_add/<int:competition_id>', methods=['GET','POST'])
# @login_required
def new_add(competition_id=None):
    form = Add_Project(competition=competition_id)
    form.subjects.choices = [(s.id, s) for s in Subject.query.all()]
    form.competition.choices = Competition.recommend()
    return render_template('new_add.html', form=form)



@project.route('/add_project/', methods=['GET','POST'])
@project.route('/add_project/<int:competition_id>/', methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute')
def add_project(competition_id=None):
    # form preprocessing
    form = Add_Project(competition=competition_id)
    form.subjects.choices = [(s.id, s) for s in Subject.query.all()]
    form.competition.choices = Competition.recommend()
    # form validation
    if form.validate_on_submit():
        subjects = [Subject.query.get(int(id)) for id in form.subjects.data]
        if form.competition.data:
            competition = Competition.query.get(int(form.competition.data))
        else:
            competition = None
        project = Project.create(
            name = form.name.data,
            oneliner=form.oneliner.data,
            summary = form.summary.data,
            subjects = subjects,
            owner = current_user,
            open = form.open.data,
            requires_application = form.requires_application.data,
            application_question = form.application_question.data,
            estimated_time = form.estimated_time.data,
            team_size = form.team_size.data,
            complete = form.complete.data,
            competition = competition
        )
        # successful message
        flash(f'Congratulations—your project, {form.name.data}, '
               'has been added!')
        task_message = True
        if form.complete.data==True:
            flash(f'As a completed project, {form.name.data} will be '
                'visible, but not joinable or editable.')
            task_message = False
        elif form.open.data==False:
            flash(f'As a closed project, {form.name.data} will be '
                  'visible and editable, but not joinable.')
        elif form.requires_application.data==False:
             flash(f'As an open project with no application, '
                   f'{form.name.data} will be available for others to '
                   'join at any time.')
        elif form.requires_application.data==True:
            flash(f'As an open project with an application, '
                  f'{form.name.data} can be joined by users you accept. '
                  'Check back soon to manage applicants.')
        if task_message:
            flash('Try adding some tasks to show what needs to '
                  'be done on your project and posting some comments '
                  "to tell people what it's all about!")
        else:
            flash('Post some comments to tell people what your project '
                  'is all about!')
        return redirect(
            url_for('project.project_page', project_code=project.code)
        )
    return render_template(
        ('add_project.html' if not request.MOBILE else 'add_mobile.html'),
        form=form
    )


@project.route('/project=<project_code>', methods=['GET', 'POST'])
@project.route('/project=<project_code>/<open_tab>', methods=['GET', 'POST'])
@limiter.limit('60/minute')
def project_page(project_code, open_tab=None):
    project = Project.query.filter_by(code=project_code).first_or_404()
    # add project to globals
    g.project = project
    # forms
    comment_form = Comment_Form(project_id=project.id)
    task_form = Task_Form(project_id=project.id) if project.is_member(current_user) else False
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
    ## forms ##
    link_form = Add_Link()
    ## subject visualization ##
    project_subjects = project.subject_data()
    ## public user stuff ##
    members = project.members.all()
    ## recommended members ##
    recommended = False
    edit_form = False
    edit_application_form = False
    show_edit_modal = False
    applications = False
    invitations = False
    if current_user==project.owner:
        applications = project.pending.all()
        invitations = project.invitations.all()
        if project.open and not project.complete:
            recommended = recommend_users(project)
        ## edit project form ##
        edit_form = Edit_Project()
        edit_application_form = Edit_Project_Application()
        edit_form.competition.choices = Competition.recommend()
        edit_form.subjects.choices = [(s.id, s) for s in Subject.query.all()]
        if request.method=='POST':
            if edit_form.validate_on_submit():
                print(edit_form.subjects.data)
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
                # subjects
                subjects = set(Subject.query.get(int(id)) for id in edit_form.subjects.data)
                if project.change_subjects(subjects):
                    edits_made = True
                # competition
                if edit_form.competition.data:
                    competition = Competition.query.get(int(edit_form.competition.data))
                    if not project.competition or project.competition!=competition:
                        project.submit_to_competition(competition)
                        edits_made = True
                if edits_made:
                    flash(f'You have successfully edited {project.name}.',
                          'success')
                    project.update()
            else:
                show_edit_modal = True
    return render_template(
            'project.html' if not request.MOBILE else 'project_mobile.html',
            project=project,
            members=members,
            applications=applications,
            invitations=invitations,
            recommended=recommended,
            comment_form=comment_form,
            task_form=task_form,
            link_form=link_form,
            activity_data=activity_data,
            authored=authored,
            completed=completed,
            project_subjects=project_subjects,
            edit_form=edit_form,
            edit_application_form=edit_application_form,
            show_edit_modal=show_edit_modal,
            open_tab=open_tab)


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
            current_user.notify(text=f'You have joined {project.name}!',
                                name=project.name,
                                redirect=project.get_url())
            project.add_member(current_user, notify_owner=True)
            return redirect(
                url_for('project.project_page', project_code=project.code)
            )
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


@project.route('/withdraw_application/<int:project_id>')
@login_required
def withdraw_application(project_id):
    ''' Withdraws current users application to project '''
    project = Project.query.get_or_404(project_id)
    if not project.reject_application(current_user, by_owner=False):
        flash('Could not withdraw application.', 'error')
    else:
        flash(f'You have withdrawn your application to {project.name}.',
              category='success')
    return redirect(request.referrer)


@project.route('/leave_project/<int:project_id>', methods=['POST'])
@login_required
def leave_project(project_id):
    ''' Leave project, transferring or deleting as necessary '''
    project = Project.query.get_or_404(project_id)
    # transfer ownership
    if (current_user==project.owner):
        if (project.members.count()>1):
            new_owner = User.query.get_or_404(request.form.get('new_owner'))
            if not project.make_owner(new_owner):
                flash('Could not transfer ownership.')
                return redirect(request.referrer)
        else:
            project.remove_member(current_user.id, by_owner=False)
            # delete all tasks to remove xps
            for task in project.tasks:
                task.delete()
            project.delete()
            flash(f'You have deleted {project.name}.')
            return redirect(
                url_for('user.user_page', code=current_user.code)
            )
    project.remove_member(current_user.id, by_owner=False)
    flash(f'You have left {project.name}.')
    return redirect(request.referrer)


@project.route('/like/<int:project_id>')
@login_required
@limiter.limit('45 per minute')
def like_action(project_id):
    ''' Star or unstar project '''
    project = Project.query.get_or_404(project_id)
    if not current_user.has_starred(project):
        current_user.star_project(project)
    else:
        current_user.unstar_project(project)
    is_starred = 1 if current_user.has_starred(project) else 0
    return jsonify({'stars':project.stars.count(), 'is_starred':is_starred})


@project.route('/project/<int:project_id>/task', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_task(project_id):
    ''' Add task to project '''
    print("HERE")
    # NOTE: CURRENTLY ASSUMES TASK IS A TO-DO TASK. IF WANT TO ADD COMPLETED, NEEDS CHANGE
    project = Project.query.get_or_404(project_id)
    form = Task_Form()
    success, html = False, ''
    if form.validate_on_submit():
        task = project.add_task(text=form.text.data, author=current_user)
        if task:
            current_user.action_xp('add_task')
            success = True
            render_task = get_template_attribute(
                                'macros/cards/task.html', 'render_todo_task'
                            )
            html = render_task(task)
    return jsonify({
        'success'   :   success,
        'html'      :   html
    })


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
@limiter.limit('45 per minute')
def change_task_status(project_id, task_id, action):
    ''' Mark task as complete, delete task, or remove help '''
    project = Project.query.get_or_404(project_id)
    if not project.change_task_status(task_id, current_user, action):
        flash('Could not update task.')
    return redirect(request.referrer)


@project.route('/remove_member/<int:project_id>/<int:user_id>')
@limiter.limit('30/minute')
def remove_member(project_id, user_id):
    ''' Removes user from project '''
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
    ''' Transfers ownership of project to user '''
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    if current_user!=project.owner:
        flash('Must be project owner to transfer ownership.')
    else:
        if not project.make_owner(user):
            flash('Could not transfer ownership', 'error')
    return redirect(request.referrer)


@project.route('/accept_application/<int:project_id>/<int:user_id>')
@limiter.limit('60/minute')
def accept_application(project_id, user_id):
    ''' Accept pending application '''
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    if current_user!=project.owner:
        flash('Must be project owner to accept applications.')
    else:
        if not project.accept_application(user):
            flash(f'Could not accept {user.name}.', 'error')
        else:
            flash(f'You have accepted {user.name}!', 'success')
    return redirect(request.referrer)


@project.route('/reject_application/<int:project_id>/<int:user_id>')
@limiter.limit('60/minute')
def reject_application(project_id, user_id):
    ''' Reject pending application '''
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    if current_user!=project.owner:
        flash('Must be project owner to reject applications.')
    else:
        if not project.reject_application(user, by_owner=True):
            flash('Could not reject applicant.', 'error')
    return redirect(request.referrer)


@project.route('/complete_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('3 per minute')
def complete_project(project_id):
    ''' Mark project as complete '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can mark a project as complete.')
    else:
        if not project.mark_complete():
            flash(f'Could not mark {project.name} as complete.', 'error')
        else:
            flash(f'Congratulations on completing {project.name}!!')
    return redirect(request.referrer)


@project.route('/uncomplete_project/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('3 per minute')
def uncomplete_project(project_id):
    ''' Mark project as incomplete '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can mark a project as incomplete.')
    else:
        if not project.mark_incomplete():
            flash(f'Could not mark {project.name} as incomplete.', 'error')
        else:
            flash(f'You have marked {project.name} as incomplete. We are '
                   'excited to see where you will take it!')
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
        if not project.mark_open():
            flash(f'Could not open {project.name}.', 'error')
        else:
            flash(f'You have opened {project.name}.', 'success')
    elif action=='close':
        if not project.mark_closed():
            flash(f'Could not close {project.name}.', 'error')
        else:
            flash(f'You have closed {project.name}.', 'success')
    return redirect(request.referrer)


@project.route('/add_application/<int:project_id>', methods=['POST'])
@login_required
@limiter.limit('10 per minute')
def add_application(project_id):
    ''' Add applicaiton to project '''
    project = Project.query.get_or_404(project_id)
    form = Edit_Project_Application()
    if current_user!=project.owner:
        flash('Only the owner can change application settings.')
    elif form.validate_on_submit():
        if not project.add_application(form.application_question.data):
            flash(f'Could not add application.', 'error')
        else:
            flash('Application requirement modified!', 'success')
    else:
        flash(f'Could not add application: {form.errors[0]}.', 'error')
    return redirect(request.referrer)


@project.route('/remove_application_requirement/<int:project_id>', methods=['POST'])
@login_required
def remove_application_requirement(project_id):
    ''' Remove application from project '''
    project = Project.query.get_or_404(project_id)
    if current_user!=project.owner:
        flash('Only the owner can change application settings.')
    else:
        if not project.remove_application():
            flash(f'Could not remove application.', 'error')
        else:
            flash('Application requirement removed!', 'success')
    return redirect(request.referrer)


## questions ##
@project.route('/add_question/<int:project_id>', methods=['POST'])
@login_required
def add_question(project_id):
    ''' Adds question (and maybe answer) to project '''
    project = Project.query.get_or_404(project_id)
    question = filter_string(request.form.get('question'))
    if not question:
        flash('Invalid question.')
    else:
        if project.is_member(current_user):
            answer = filter_string(request.form.get('answer'))
            project.add_question(question, answer)
        else:
            project.add_question(question)
        flash('Question added!', 'success')
    return redirect(request.referrer)


@project.route('/edit_answer/<int:project_id>/<int:question_id>', methods=['POST'])
@limiter.limit('30/min')
@login_required
def edit_answer(project_id, question_id):
    project = Project.query.get_or_404(project_id)
    question = project.questions.filter_by(id=question_id).first()
    if not question:
        flash('Could not find question.', category='error')
    elif not project.is_member(current_user):
        flash('Only project members can answer questions.', category='error')
    else:
        question.add_answer(answer=request.form.get('answer'))
        flash('Question answered.', category='success')
    return redirect(request.referrer)


@project.route('/delete_question/<int:project_id>/<int:question_id>')
@login_required
def delete_question(project_id, question_id):
    ''' Adds question (and maybe answer) to project '''
    project = Project.query.get_or_404(project_id)
    if project.is_member(current_user):
        if project.remove_question(question_id):
            flash('Question removed.', 'success')
        else:
            flash('Could not remove question.', 'error')
    else:
        flash('Cannot delete question because you are not a project member.',
              category='error')
    return redirect(request.referrer)


## urls ##
@project.route('/add_link/<int:project_id>/<int:public>/<int:category>', methods=['POST'])
@login_required
@limiter.limit('20/minute')
def add_link(project_id, public, category):
    ''' Adds link to project '''
    project = Project.query.get_or_404(project_id)
    public = True if (public==1) else False
    form = Add_Link()
    if not project.is_member(current_user):
        flash('Could not add link because you are not a project member.',
            category='error')
    elif not public and not project.is_owner(current_user):
        flash('Only the project owner can add private links.', 'error')
    elif form.validate_on_submit():
        url = form.link.data
        if url:
            project.add_link(url, public=public, category=category)
            flash('Link added!', 'success')
        else:
            flash('Invalid link.', 'error')
    else:
        flash('Invalid link.', 'error')
    return redirect(request.referrer)


@project.route('/remove_link/<int:project_id>/<int:link_id>', methods=['GET'])
@login_required
def remove_link(project_id, link_id):
    ''' Adds link to project '''
    project = Project.query.get_or_404(project_id)
    if not project.is_member(current_user):
        flash('Could not remove link because you are not a project member.',
            category='error')
    else:
        if project.remove_link(link_id):
            flash('Link removed.', 'success')
        else:
            flash('Could not remove link.', 'error')
    return redirect(request.referrer)


@project.route('/save_instructions/<int:project_id>', methods=['GET', 'POST'])
def save_instructions(project_id):
    ''' Saves project instructions '''
    project = Project.query.get_or_404(project_id)
    if not project.is_member(current_user):
        flash('Could not edit instructions because you are not a project member.',
            category='error')
    else:
        instructions = request.json.get('data')
        if instructions is not None:
            project.instructions = instructions
            project.update()
    return jsonify({})
