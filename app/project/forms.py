from flask import url_for
from wtforms import (TextField, StringField, BooleanField, SelectField,
                    SelectMultipleField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)
# absolute imports
from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator
from app.link.utils import fix_url
# package imports
from .models import Project


class Add_Project(BaseForm):
    name = StringField(label='Project Name',
                       validators=[DataRequired(), Length(1, 40)],
                       description='Give your project a name!',
                       render_kw={'placeholder':'TheProjectProject',
                                  'max': 30})
    oneliner = StringField(label='One-Liner',
                           validators=[DataRequired(), Length(1, 100)],
                           description='One line description of your project.',
                           render_kw={'placeholder':'Facilitate collaboration on projects.',
                                      'max': 40})
    summary = TextAreaField(label='Summary',
                        validators=[DataRequired(), Length(1, 400)],
                        description='Describe your project in more detail.',
                        render_kw={'placeholder': ('TheProjectProject is founded...'),
                                  'max':400})
    # url = StringField(label='URL',
                    # validators=[Length(0, 128)],
                    # description=('You can link media (eg. a Github, website, '
                                 # 'doc, etc.) to showcase your progress.'),
                    # render_kw={'placeholder':'https://www.github.com/me/example', 'max':128})
    subjects = SelectMultipleField('Subjects',
                                    description=('What subjects might this '
                                                'project involve?'),
                                    validators=[Select_Limit_Validator(5)],
                                    choices=[], coerce=int,
                                    render_kw={'max':5})
    open = BooleanField('Team Project',
                        validators=[],
                        description=('Whether you want to work with others on this project.'))
    requires_application = BooleanField('Requires Application',
                            validators=[],
                            description=('Applications allow you to choose '
                                         'who joins the project.'))
    application_question = TextField('Application Question',
                                validators=[Length(0, 128)],
                                description=('Add a question to screen '
                                            'applicants.'),
                                render_kw={'placeholder':'What do you look for in a team?',
                                           'max':128})
    estimated_time = IntegerField('Estimated Time',
                                  description=('We are all about fast, impactful '
                                            'projects. You will be able to extend this '
                                            'time later if you need.'),
                                  render_kw={'min':0, 'max':30, 'start':7})
    team_size = IntegerField('Target Team Size',
                            description=('What size do you want your team to be?'),
                            render_kw={'min':2, 'max':40, 'start':5})
    complete = BooleanField('Completed',
                            description=('Whether the project has been '
                            'completed.'))
    competition = SelectField('Competition',
                            validators=[],
                            description=('Submit your project to '
                                        'competitions and win rewards! Please '
                                        'make sure you meet criteria.'),
                            choices=[]
                            # coerce=int
                        )

    def validate(self):
        ''' Validates project '''
        # error flag to check all errors at once
        error_flag = False
        # stock validation
        rv = BaseForm.validate(self)
        if not rv:
            error_flag = True
        if (len(self.subjects.data)>5):
            self.subjects.errors = ['Can only choose up to 5 subjects.']
            error_flag = True
        # team size defaults to 1 if None
        if self.team_size.data is None:
            self.team_size.data = 1
        return (not error_flag)


class Edit_Project(BaseForm):
    ''' Form to edit existing project '''
    name = StringField(label='Project Name',
                       validators=[DataRequired(), Length(1, 25)],
                       render_kw={'max': 25})
    oneliner = StringField(label='One-Liner',
                           validators=[DataRequired(), Length(1, 40)],
                           render_kw={'max': 40})
    summary = TextField(label='Summary',
                        validators=[DataRequired(), Length(1, 400)],
                        render_kw={'max':400})
    estimated_time = FloatField('Estimated Time', render_kw={'min':0, 'max':30, 'start':7})
    team_size = IntegerField('Target Team Size',
                            render_kw={'min':1, 'max':30, 'start':7})
    competition = SelectField('Competition',
                            validators=[],
                            description=('Submit your project to '
                                        'competitions and win rewards! Please '
                                        'make sure you meet criteria.'),
                            choices=[],
                            # coerce=int
                        )


class Edit_Project_Application(BaseForm):
    ''' Form to edit application question of existing project '''
    application_question = TextField('Application Question',
                                    validators=[Length(0, 128)],
                                    render_kw={'max':128})



class Project_Application_Form(BaseForm):
    ''' Form to respond to question on existing project application '''
    response = TextField('Response', validators=[Length(0,250)],
                         render_kw={'max':250})


class Task_Form(BaseForm):
    ''' Form to add task to project '''
    text = TextField(
        'Task',
        validators=[DataRequired(), Length(1,160)],
        render_kw={'max':160}
    )

    def __init__(self, *args, **kwargs):
        super(Task_Form, self).__init__()
        project_id = kwargs.get('project_id')
        if project_id:
            self.text.render_kw['action'] = url_for('project.add_task', project_id=project_id)


class Comment_Form(BaseForm):
    ''' Form to add comment to project '''
    text = TextField('Comment', validators=[DataRequired(), Length(1,160)],
                     render_kw={'max':160})

    def __init__(self, *args, **kwargs):
        super(Comment_Form, self).__init__()
        project_id = kwargs.get('project_id')
        if project_id:
            self.text.render_kw['action'] = url_for('project.add_comment', project_id=project_id)


class URL_Form(BaseForm):
    ''' Form to add url to project '''
    text = StringField('URL', validators=[DataRequired(), Length(1, 500)],
                       render_kw={'max':500})
