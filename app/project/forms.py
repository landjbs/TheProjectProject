from wtforms import (TextField, StringField, BooleanField,
                    SelectMultipleField, FloatField, IntegerField,
                    TextAreaField, validators)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)
# absolute imports
from app.forms.base import BaseForm
# package imports
from .models import Project


class Add_Project(BaseForm):
    name = StringField(label='Project Name',
                       validators=[DataRequired(), Length(1, 25)],
                       description='Give your project a name!',
                       render_kw={'placeholder':'TheProjectProject',
                                  'max': 25})
    oneliner = StringField(label='One-Liner',
                           validators=[DataRequired(), Length(1, 40)],
                           description='One line description of your project.',
                           render_kw={'placeholder':'Project building community.',
                                      'max': 40})
    summary = TextAreaField(label='Summary',
                        validators=[DataRequired(), Length(1, 400)],
                        description='Describe your project in more detail.',
                        render_kw={'placeholder': ('I need help designing this '
                                                   'online community of '
                                                   'builders...'),
                                  'max':400})
    url = StringField(label='URL',
                    validators=[Length(0, 128)],
                    description=('You can link media (eg. a Github, website, '
                                 'doc, etc.) to showcase your progress.'),
                    render_kw={'placeholder':'https://www.github.com/me/example', 'max':128})
    subjects = SelectMultipleField('Subjects',
                                    description=('What subjects might this '
                                                'project involve?'),
                                    validators=[Select_Limit_Validator(5)],
                                    choices=[], #list(subjects),
                                    render_kw={'max':5})
    open = BooleanField('Open',
                        validators=[],
                        description=('Open projects can have team members.'))
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
                                  description=('How long you '
                                  'think the project might take.'),
                                  render_kw={'min':0, 'max':30, 'start':7})
    team_size = IntegerField('Target Team Size',
                            description=('The biggest you want your '
                                         'team to be.'),
                            render_kw={'min':1, 'max':30, 'start':7})
    complete = BooleanField('Completed',
                            description=('Whether the project has been '
                            'completed.'))
    print('WARNING: TEAM_SIZE AND ESTIMATE_TIME INTEGER RENDER BUG!!!')
