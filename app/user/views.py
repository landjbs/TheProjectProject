from flask import request, redirect, url_for, render_template, flash, g
from flask_babel import gettext
from flask_login import login_required
from app.user.models import User
# from .forms import EditUserForm

from ..user import user



@application.route('/user=<code>', methods=['GET', 'POST'])
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
    # sum stars
    stars = 0
    for project in user.projects:
        stars += project.stars.count()
    # subjects
    subject_data = {s.subject.name : s.number for s in user.subjects[:10]}
    ## forms ##
    # application to projects
    project_application = forms.Project_Application_Form(request.form)
    # edit user account
    show_edit_modal = False
    edit_form = forms.Edit_User(request.form) if (current_user==user) else False
    if request.method=='POST':
        if edit_form.validate_on_submit():
            edits_made = False
            # name
            new_name = edit_form.name.data
            if new_name!=user.name:
                user.name = new_name
                edits_made = True
            # email
            # new_email = edit_form.email.data
            # if new_email!=user.email:
            #     user.email = new_email
            #     edits_made = True
            # github
            new_github = edit_form.github.data
            if new_github!=user.github:
                user.github = new_github
                edits_made = True
            # about
            new_about = edit_form.about.data
            if new_about!=user.about:
                user.about = new_about
                edits_made = True
            # new password
            if edit_form.password.data!='':
                if not user.check_password(edit_form.password.data):
                    user.password = user.set_password(edit_form.password.data)
                    edits_made = True
            if edits_made:
                flash('You have successfully edited your acount.')
                db.session.add(user)
                db.session.commit()
                db.session.close()
        else:
            show_edit_modal = True
    return render_template('user.html', user=user, stars=stars,
                            task_data=task_data, subject_data=subject_data,
                            owned_tabs=owned_tabs, member_tabs=member_tabs,
                            project_application=project_application,
                            edit_form=edit_form,
                            show_edit_modal=show_edit_modal)
