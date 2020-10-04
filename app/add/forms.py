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
from markupsafe import Markup
# from app.company.models import Company


class Add_Shared(BaseForm):
    ''' Fields of Add form that are shared between all types '''
    identifier = 'Add_Shared'
    # type
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
                    'icon'  :   'fa fa-circle',
                    'action':   "set_type('Project'); hide_class('company');"
                },
                2:  {
                    'key'   :   'B',
                    'icon'  :   'fa fa-briefcase',
                    'action':   "set_type('Company'); hide_class('project');"
                }
            },
            'seconds':  3
        }
    )
    # name
    name = StringField(
        label=Markup("<span class='project_type'></span> Name"),
        validators=[DataRequired(), Length(1, 40)],
        description='Give your idea a name!',
        render_kw={
            'placeholder':  'TheProjectProject',
            'max':          30,
            'seconds':      5
        }
    )
    # oneliner
    oneliner = StringField(
        label='One Line',
        validators=[DataRequired(), Length(1, 100)],
        description=Markup('One line description of your <span class="project_type lowercase"></span>.'),
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
        description=Markup('Describe your <span class="project_type lowercase"></span> in more detail.'),
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
        description=Markup('What subjects might this <span class="project_type lowercase"></span> involve?'),
        validators=[],
        choices=[],
        coerce=int,
        render_kw={
            'seconds':  8
        }
    )
    ### COMPANY ###
    # has_raised
    has_raised = BooleanField(
                    label='Have you raised any funding so far?',
                    description='',
                    render_kw={
                        'seconds':  5,
                        'tabclass': 'company',
                        'datamap': {
                            'true': {
                                'action':   ''
                            },
                            'false': {
                                'action':   "hide_class('has_raised');"
                            }
                        }
                    }
                )
    # amount_raised
    amount_raised = IntegerField(
                        label='Roughly how much have you raised?',
                        validators=[],
                        description='',
                        render_kw={
                            'min':      1,
                            'start':    5000,
                            'max':      1000000, # current max $100 mil
                            'optional': True,
                            'seconds':  5,
                            'tabclass': 'company has_raised'
                        }
                    )
    # looking for funding
    looking_for_funding = BooleanField(
                            label='Are you currently looking for funding?',
                            validators=[],
                            render_kw={
                                'tabclass': 'company',
                                'datamap': {
                                    'true': {
                                        'action':   ''
                                    },
                                    'false': {
                                        'action':   ''
                                    }
                                }
                            }
    )
    ### PROJECT ###
    complete = BooleanField(
                label='Have you already completed this project?',
                validators=[],
                description='',
                render_kw={
                    'seconds':  5,
                    'tabclass': 'project',
                    'datamap': {
                        'true':  {
                            'action':   "hide_class('incomplete');"
                        },
                        'false':  {
                            'action':   "hide_class('complete'); hide_class('looking_for_team');"
                        }
                    }
                }
    )
    ### COMPLETED PROJECT ###
    time_it_took = IntegerField(
                    label='Roughly how many days did it take?',
                    validators=[],
                    description='',
                    render_kw={
                        'min':      1,
                        'start':    30,
                        'max':      360,
                        'units':     'days',
                        'seconds':  5,
                        'tabclass': 'project complete'
                    }
    )
    ### INCOMPLETE PROJECT ###
    estimated_time = IntegerField(
                        label='Roughly how many days do you expect it to take?',
                        validators=[],
                        description='TheProjectProject is all about short, impactful projects. You will be able to extend this time later, if you wish.',
                        render_kw={
                            'min':      1,
                            'start':    7,
                            'max':      60,
                            'units':    'days',
                            'tabclass': 'project incomplete'
                        }
    )
    ### SHARED TEAM BUILDING ###
    working_with_others = BooleanField(
        label='Have you been working with anyone else?',
        description='',
        validators=[],
        render_kw={
            'tabclass': '',
            'datamap': {
                'true': {
                    'action':   ''
                },
                'false': {
                    'action':   "hide_class('other_members');"
                }
            }
        }
    )
    # TODO: add querying for others
    # others =
    ### INCOMPLETE PROJECT AND COMPANY TEAM BUILDING ###
    looking_for_team = BooleanField(
        label='Are you looking for new team members?',
        description='',
        validators=[],
        render_kw={
            'tabclass': 'incomplete',
            'datamap': {
                'true': {
                    'action':   ''
                },
                'false': {
                    'action':   "hide_class('looking_for_team')"
                }
            }
        }
    )
    target_team_size = IntegerField(
        label='Roughly how many team members are you looking for?',
        description='',
        validators=[],
        render_kw={
            'min':      1,
            'start':    7,
            'max':      20,
            'units':    'people',
            'tabclass': 'looking_for_team'
        }
    )
    requires_application = BooleanField(
        label='Would you like to create an application to join your project?',
        description='WARNING blah blah blha______',
        validators=[],
        render_kw={
            'tabclass': 'project looking_for_team',
            'datamap': {
                'true': {
                    'action':   ''
                },
                'false': {
                    'action':   'hide_class("application")'
                }
            }
        }
    )
    application_question = StringField(
        label=Markup('Ask applicants to your <span class="project_type lowercase"></span> a question.'),
        description=Markup('Members who want to join your <span class="project_type lowercase"></span> will have to answer this question. You will be able to see what they say when evaluating their application.'),
        validators=[Length(0, 128)],
        render_kw={
            'placeholder':  '',
            'max': 128,
            'tabclass': 'looking_for_team application'
        }
    )



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
