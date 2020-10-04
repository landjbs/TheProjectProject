from flask import url_for
from wtforms import (TextField, StringField, BooleanField, SelectField,
                    SelectMultipleField, FloatField, IntegerField,
                    TextAreaField, validators, Field, )
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)
# absolute imports
from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator
from app.link.utils import fix_url
# package imports
from app.project.models import Project
# from app.company.models import Company


class Fragment(BaseForm):
    ''' Fragment of form that points to next based on data '''
    def get_next_fragment(self):
        return None



class Add_Type(Fragment):
    identifier = 'Add_Type'
    
    type = SelectField(
        label='What are you working on?',
        validators=[DataRequired()],
        description='',
        choices=[(1, 'Project'), (2, 'Company')],
        render_kw={
            'optional': False,
            'datamap': {
                1:  {
                    'key'   :   'A',
                    'icon'  :   'fa fa-circle'
                },
                2:  {
                    'key'   :   'B',
                    'icon'  :   'fa fa-briefcase'
                }
            },
            'seconds':  3
        }
    )

    def get_next_fragment(self):
        return Add_Shared



# class Add_Shared(Fragment):
    # def __init__(self):



class Add_Shared(BaseForm):
    ''' Fields of Add form that are shared between all types '''
    identifier = 'Add_Shared'
    # name
    name = StringField(
        label='Project Name',
           validators=[DataRequired(), Length(1, 40)],
           description='Give your project a name!',
           render_kw={
            'placeholder':  'TheProjectProject',
            'max':          30,
            'seconds':      5
        }
    )
    # oneliner
    oneliner = StringField(
        label='One-Liner',
        validators=[DataRequired(), Length(1, 100)],
        description='One line description of your project.',
        render_kw={
            'placeholder':'The platform for sharing, collaborating on, and publicizing independent projects.',
            'max': 40,
            'seconds':  20
        }
    )
    # summary
    summary = TextAreaField(
        label='Summary',
        validators=[DataRequired(), Length(1, 400)],
        description='Describe your project in more detail.',
        render_kw={
            'placeholder': ('TheProjectProject is a virtual community of innovators, who collaborate on projects across a wide range of fields and time windows. '
                            'I need a team of web developers, database experts, and creative minds to help me build this platform. We will tackle interesting problems '
                            'such as matching users with projects they will like and designing an interface that helps people communicate their ideas...'),
            'max':400,
            'seconds':  90
        }
    )
    # subjects
    subjects = SelectMultipleField(
        label='Subjects',
        description='What subjects might this project involve?',
        validators=[],
        choices=[],
        coerce=int,
        render_kw={
            'seconds':  8
        }
    )

    def get_next_fragment(self):
        print(self.project_type.data)
        if (self.project_type.data=='2'):
            return Add_Company()
        else:
            raise ValueError('')

    def total_time(self):
        time = 0
        for field in self:
            try:
                time += field.render_kw['seconds']
            except:
                print(f'WARNING: {field.name} has no render_kw')
        return time


class Add_Company(BaseForm):
    '''
    Fields of add form used to build Company objects
    '''
    ## raising ##
    # has_raised
    has_raised = BooleanField(
                    label='Have you raised any funding so far?',
                    validators=[DataRequired()],
                    description='',
                    render_kw={
                        'optional': False,
                        'default':  False,
                        'seconds':  5
                    }
                )
    # amount_raised
    amount_raised = IntegerField(
                        label='Roughly how much have you raised?',
                        validators=[DataRequired()],
                        description='',
                        render_kw={
                            'min':      1,
                            'start':    5000,
                            'max':      1000000, # current max $100 mil
                            'optional': True,
                            'seconds':  5
                        }
                    )
    # # looking_to_raise
    # looking_to_raise = BooleanField(
    #                     label='Are you currently looking for funding?',
    #                     validators=[DataRequired()],
    #                     description='',
    #                     render_kw={
    #                         'optional': True
    #                     }
    #                 )
    # ## team building ##
    # # looking_for_members
    # looking_for_members = BooleanField(
    #                         label='Are you currently looking for team members?',
    #                         validators=[DataRequired()],
    #                         description='',
    #                         render_kw={
    #                             'optional': False
    #                         }
    #                     )
    # # application question
    # application_question = StringField(
    #                         label='Ask a question to applicants who want to join the team.',
    #                         validators=[DataRequired()],
    #                         description='',
    #                         render_kw={
    #                             'optional': False
    #                         }
    # )



class Add_Comp(BaseForm):
    '''
    Dynamic add form. Currently supports Project and Company
    '''
    ## SHARED FIELDS ##
    ## PROJECT FIELDS
    complete = BooleanField('Completed',
                            description=('Whether the project has been '
                            'completed.'))
    open = BooleanField('Team Project',
            validators=[],
            description=('Whether you want to work with others on this project.')
    )
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
    ## COMPANY FIELDS
    # funding
